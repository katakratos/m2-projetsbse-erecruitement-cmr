from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from .models import Job, Criteria, AHPPriority, CandidateData
from applications.models import Application  # Fixed import - Application from applications app
from .forms import JobForm, CriteriaForm, AHPMatrixForm
from .ahp_utils import get_all_criteria, calculate_consistency_ratio, generate_consistent_ahp_matrix
from users.models import Employer
import numpy as np
import json
from django.http import JsonResponse
from .utils.ranking import recalculate_ahp_ranks_for_job
from django.db import transaction
# Import the Celery task
from .tasks import process_job_applications_task
# Add this import
from .utils.genetic_algorithm import optimize_team_for_job
from django.core.paginator import Paginator
from .filters import JobFilter

class JobListView(View):
    def get(self, request):
        # Get all jobs
        jobs = Job.objects.all()
        
        # Apply filters
        job_filter = JobFilter(request.GET, queryset=jobs)
        filtered_jobs = job_filter.qs
        
        # Calculate the total count before pagination
        total_jobs_count = filtered_jobs.count()
        
        # Count for experience levels (for sidebar display)
        entry_level_count = Job.objects.filter(experience='Entry').count()
        intermediate_count = Job.objects.filter(experience='Intermediate').count()
        expert_count = Job.objects.filter(experience='Expert').count()
        
        # Get selected filter values for maintaining state in template
        selected_types = request.GET.getlist('type')
        selected_experience = request.GET.getlist('experience')
        
        # Pagination
        paginator = Paginator(filtered_jobs, 10)  # Show 10 jobs per page
        page_number = request.GET.get('page', 1)
        jobs_page = paginator.get_page(page_number)
        
        context = {
            'jobs': jobs_page,
            'jobs_count': total_jobs_count,  # Add this line to pass the total count
            'job_filter': job_filter,
            'selected_types': selected_types,
            'selected_experience': selected_experience,
            'entry_level_count': entry_level_count,
            'intermediate_count': intermediate_count,
            'expert_count': expert_count,
            'is_paginated': paginator.num_pages > 1,
            'paginator': paginator,
            'page_obj': jobs_page,
        }
        
        return render(request, 'jobs/job_list.html', context)

class JobDetailView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        criteria = job.criteria_set.all()
        
        # Check if logged in user has applied for this job
        has_applied = False
        application_status = None
        if request.user.is_authenticated and hasattr(request.user, 'jobseeker'):
            application = job.applications.filter(jobseeker=request.user.jobseeker).first()
            has_applied = application is not None
            if has_applied:
                application_status = application.status
            
        # Check for AHP priority weights
        weights_display = []
        if hasattr(job, 'ahp_priority'):
            try:
                ahp = job.ahp_priority
                if ahp.criteria_names and ahp.weights:
                    # Format weights for display
                    weights_display = [(name, float(weight)*100) for name, weight in zip(ahp.criteria_names, ahp.weights)]
                    weights_display.sort(key=lambda x: x[1], reverse=True)  # Sort by weight descending
            except Exception as e:
                print(f"Error getting AHP data: {e}")
                
        # Check processing status if user is employer
        processing_status = None
        if request.user.is_authenticated and hasattr(request.user, 'employer') and request.user.employer == job.employer:
            total_applications = job.applications.count()
            processed_applications = job.candidate_data.count() if hasattr(job, 'candidate_data') else 0
            
            if processed_applications > 0:
                if processed_applications >= total_applications:
                    processing_status = 'completed'
                else:
                    processing_status = 'partial'
            elif total_applications > 0:
                processing_status = 'pending'
        
        return render(request, 'jobs/job_detail.html', {
            'job': job, 
            'criteria': criteria,
            'weights_display': weights_display,
            'has_applied': has_applied,
            'application_status': application_status,
            'processing_status': processing_status
        })

@method_decorator(login_required, name='dispatch')
class JobCreateView(View):
    def get(self, request):
        if not hasattr(request.user, 'employer'):
            messages.error(request, "Only employers can create job listings.")
            return redirect('job_list')
        
        form = JobForm()
        return render(request, 'jobs/job_form.html', {'form': form})
    
    def post(self, request):
        if not hasattr(request.user, 'employer'):
            messages.error(request, "Only employers can create job listings.")
            return redirect('job_list')
        
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employer
            job.save()
            messages.success(request, "Job listing created successfully.")
            return redirect('job_detail', job_id=job.id)
        
        return render(request, 'jobs/job_form.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class JobUpdateView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to edit this job.")
            return redirect('job_list')
        
        form = JobForm(instance=job)
        return render(request, 'jobs/job_form.html', {'form': form, 'job': job})
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to edit this job.")
            return redirect('job_list')
        
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job listing updated successfully.")
            return redirect('job_detail', job_id=job.id)
        
        return render(request, 'jobs/job_form.html', {'form': form, 'job': job})

@method_decorator(login_required, name='dispatch')
class AddCriteriaView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to add criteria to this job.")
            return redirect('job_list')
        
        form = CriteriaForm()
        criteria = job.criteria_set.all()  # Get existing criteria
        return render(request, 'jobs/add_criteria.html', {'form': form, 'job': job, 'criteria': criteria})
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to add criteria to this job.")
            return redirect('job_list')
        
        form = CriteriaForm(request.POST)
        if form.is_valid():
            criteria_text = form.cleaned_data['multiple_criteria']
            # Split by lines and filter out empty lines
            criteria_list = [line.strip() for line in criteria_text.split('\n') if line.strip()]
            
            # Create a criteria object for each line
            created_count = 0
            for criterion in criteria_list:
                if len(criterion) <= 255:  # Enforce max_length
                    Criteria.objects.create(job=job, criteria=criterion)
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f"{created_count} criteria added successfully.")
            else:
                messages.warning(request, "No valid criteria were submitted.")
                
            return redirect('add_criteria', job_id=job.id)  # Redirect back to add more criteria
        
        criteria = job.criteria_set.all()  # Get existing criteria in case of form errors
        return render(request, 'jobs/add_criteria.html', {'form': form, 'job': job, 'criteria': criteria})

@method_decorator(login_required, name='dispatch')
class AHPMatrixView(View):
    """View for creating and processing AHP matrices for job criteria"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to set criteria priorities for this job.")
            return redirect('job_list')
        
        # Get all criteria for this job
        criteria_list = get_all_criteria(job)
        
        if len(criteria_list) < 2:
            messages.warning(request, "You need at least 2 criteria to create a priority matrix. Please add more criteria.")
            return redirect('add_criteria', job_id=job.id)
        
        # Check if job already has an AHP priority matrix
        ahp_priority = None
        weights_display = []
        form = None
        auto_generated = False
        
        try:
            # Try to get existing AHP priority
            ahp_priority = job.ahp_priority
            
            # If found, pre-fill form with existing matrix values
            initial_data = {}
            matrix_data = ahp_priority.matrix_data
            criteria_keys = ahp_priority.criteria_keys
            
            for i, key_i in enumerate(criteria_keys):
                for j, key_j in enumerate(criteria_keys):
                    if i < j:
                        value = matrix_data[i][j]
                        field_name = f"{key_i}__{key_j}"
                        
                        # Convert to string format for the form
                        if value < 1:
                            initial_data[field_name] = f"1/{int(1/value)}" if 1/value == int(1/value) else f"1/{round(1/value, 1)}"
                        else:
                            initial_data[field_name] = str(int(value)) if value == int(value) else str(round(value, 1))
            
            # Create form with pre-filled data
            form = AHPMatrixForm(criteria_list=criteria_list, initial=initial_data)
            
            # Format weights for display
            if ahp_priority.criteria_names and ahp_priority.weights:
                weights_display = [(name, float(weight)*100) for name, weight in zip(ahp_priority.criteria_names, ahp_priority.weights)]
                weights_display.sort(key=lambda x: x[1], reverse=True)  # Sort by weight descending
                
        except (Job.ahp_priority.RelatedObjectDoesNotExist, AttributeError):
            # No existing AHP priority - generate a new consistent one automatically
            print("No existing AHP priority found. Generating new consistent matrix...")
            
            # Generate consistent matrix
            weights, matrix_data = generate_consistent_ahp_matrix(criteria_list)
            
            # Create a new AHPPriority
            criteria_keys = [c[0] for c in criteria_list]
            criteria_names = [c[1] for c in criteria_list]
            
            try:
                # Calculate consistency to double-check
                matrix_np = np.array(matrix_data)
                cr, is_consistent, _, _ = calculate_consistency_ratio(matrix_np)
                
                # Create and save new AHPPriority
                ahp_priority = AHPPriority.objects.create(
                    job=job,
                    matrix_data=matrix_data,
                    criteria_keys=criteria_keys,
                    criteria_names=criteria_names,
                    weights=weights,
                    consistency_ratio=float(cr),
                    is_consistent=is_consistent
                )
                
                # Format matrix for form
                initial_data = {}
                for i, key_i in enumerate(criteria_keys):
                    for j, key_j in enumerate(criteria_keys):
                        if i < j:
                            value = matrix_data[i][j]
                            field_name = f"{key_i}__{key_j}"
                            
                            # Convert to string format for the form
                            if value < 1:
                                initial_data[field_name] = f"1/{int(1/value)}" if 1/value == int(1/value) else f"1/{round(1/value, 1)}"
                            else:
                                initial_data[field_name] = str(int(value)) if value == int(value) else str(round(value, 1))
                
                # Create form with pre-filled data
                form = AHPMatrixForm(criteria_list=criteria_list, initial=initial_data)
                
                # Format weights for display
                weights_display = [(name, float(weight)*100) for name, weight in zip(criteria_names, weights)]
                weights_display.sort(key=lambda x: x[1], reverse=True)  # Sort by weight descending
                
                # Set flag to show auto-generation message
                auto_generated = True
                
                messages.info(request, "We've automatically generated a consistent AHP matrix for you. Feel free to adjust the values if needed.")
                
            except Exception as e:
                print(f"Error generating initial AHP priority: {e}")
                # If generation fails, just create an empty form
                form = AHPMatrixForm(criteria_list=criteria_list)
                messages.warning(request, "Could not automatically generate a consistent matrix. Please fill in the values manually.")
        
        except Exception as e:
            print(f"Error loading AHP data: {e}")
            form = AHPMatrixForm(criteria_list=criteria_list)
        
        # If form is still None for some reason (failsafe)
        if form is None:
            form = AHPMatrixForm(criteria_list=criteria_list)
        
        return render(request, 'jobs/ahp_matrix.html', {
            'form': form,
            'job': job,
            'criteria': criteria_list,
            'weights_display': weights_display,
            'auto_generated': auto_generated
        })
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to set criteria priorities for this job.")
            return redirect('job_list')
        
        # Get all criteria for this job
        criteria_list = get_all_criteria(job)
        
        if len(criteria_list) < 2:
            messages.warning(request, "You need at least 2 criteria to create a priority matrix. Please add more criteria.")
            return redirect('add_criteria', job_id=job.id)
        
        # Debug: Print all POST data to see what's being submitted
        print("Form POST data:", request.POST)
        
        # Create and validate form
        form = AHPMatrixForm(criteria_list=criteria_list, data=request.POST)
        
        # Try to generate the matrix and calculate consistency regardless of form validity
        try:
            # Create a matrix from the submitted values (even if form has other validation errors)
            matrix = np.ones((len(criteria_list), len(criteria_list)))
            
            # Parse the form data manually to build the matrix
            for i, (id_i, _) in enumerate(criteria_list):
                for j, (id_j, _) in enumerate(criteria_list):
                    if i < j:
                        field_name = f"{id_i}__{id_j}"
                        value_str = request.POST.get(field_name, '1')
                        
                        # Parse the value (handles fractions like 1/3)
                        try:
                            if '/' in value_str:
                                num, denom = value_str.split('/')
                                value = float(num) / float(denom)
                            else:
                                value = float(value_str)
                                
                            matrix[i, j] = value
                            matrix[j, i] = 1.0 / value
                        except (ValueError, ZeroDivisionError) as e:
                            print(f"Error parsing value for {field_name}: {e}")
            
            # Save the matrix for debug and potential reuse
            request.session[f'debug_matrix_{job_id}'] = matrix.tolist()
            
            # Calculate consistency ratio and weights
            print("Calculating consistency ratio...")
            cr, is_consistent, suggestions, weights = calculate_consistency_ratio(matrix)
            print(f"Consistency results: CR={cr}, is_consistent={is_consistent}")
            
            # Add consistency information to the template context
            consistency_info = {
                'calculated': True,
                'cr': cr,
                'is_consistent': is_consistent,
                'message': f"The priority matrix {'is' if is_consistent else 'is not'} consistent (CR = {cr:.4f}{'<0.1' if is_consistent else '>0.1'})"
            }
            
            # Even if the form has other validation issues, we can still display consistency results
            if form.is_valid():
                # Save to the AHPPriority model regardless of consistency
                criteria_keys = [c[0] for c in criteria_list]
                criteria_names = [c[1] for c in criteria_list]
                
                try:
                    # Create or update the AHP priority
                    ahp_priority, created = AHPPriority.objects.update_or_create(
                        job=job,
                        defaults={
                            'matrix_data': matrix.tolist(),
                            'criteria_keys': criteria_keys,
                            'criteria_names': criteria_names,
                            'weights': weights,
                            'consistency_ratio': float(cr),
                            'is_consistent': is_consistent
                        }
                    )
                    print(f"AHP Priority saved: created={created}")
                    
                    if is_consistent:
                        messages.success(request, f"The priority matrix is consistent (CR = {cr:.4f} < 0.1) and has been saved.")
                        return redirect('job_detail', job_id=job.id)
                    else:
                        # Store suggestions in session for the suggestion view
                        suggestion_data = {
                            'cr': cr,
                            'suggestions': {f"{k[0]},{k[1]}": v for k, v in suggestions.items()}
                        }
                        request.session[f'ahp_suggestions_{job_id}'] = json.dumps(suggestion_data)
                        request.session[f'ahp_matrix_{job_id}'] = matrix.tolist()
                        
                        messages.warning(request, f"Your priority matrix is inconsistent (CR = {cr:.4f} > 0.1). Please review the suggested changes.")
                        return redirect('ahp_matrix_suggestions', job_id=job_id)
                        
                except Exception as e:
                    print(f"Error saving AHP Priority: {e}")
                    messages.error(request, f"Error saving AHP Priority: {str(e)}")
            else:
                # Form has validation errors
                print("Form is invalid. Errors:", form.errors)
                messages.error(request, "Please correct the errors in the form and try again.")
        
        except Exception as e:
            # If matrix generation or consistency calculation fails
            print(f"Error processing matrix: {e}")
            messages.error(request, f"Error processing priority matrix: {str(e)}")
            consistency_info = {
                'calculated': False,
                'message': f"Could not calculate consistency: {str(e)}"
            }
        
        # Get existing weights for display if available
        weights_display = []
        try:
            if hasattr(job, 'ahp_priority'):
                ahp_priority = job.ahp_priority
                if ahp_priority.criteria_names and ahp_priority.weights:
                    weights_display = [(name, float(weight)*100) for name, weight in zip(ahp_priority.criteria_names, ahp_priority.weights)]
                    weights_display.sort(key=lambda x: x[1], reverse=True)
        except Exception as e:
            print(f"Error loading weights: {e}")
            
        # If we have consistency info from this attempt, create weights display from it
        if 'consistency_info' in locals() and consistency_info['calculated'] and 'weights' in locals():
            # Format weights for display from the current calculation
            try:
                calculated_weights = [(name, float(weight)*100) for name, weight in zip([c[1] for c in criteria_list], weights)]
                calculated_weights.sort(key=lambda x: x[1], reverse=True)
                # Add to context
                return render(request, 'jobs/ahp_matrix.html', {
                    'form': form,
                    'job': job,
                    'criteria': criteria_list,
                    'weights_display': calculated_weights,
                    'consistency_info': consistency_info
                })
            except Exception as e:
                print(f"Error formatting calculated weights: {e}")
        
        # Return with the existing weights if available
        return render(request, 'jobs/ahp_matrix.html', {
            'form': form,
            'job': job,
            'criteria': criteria_list,
            'weights_display': weights_display,
            'consistency_info': locals().get('consistency_info', {'calculated': False, 'message': "No consistency information available"})
        })

@method_decorator(login_required, name='dispatch')
class AHPSuggestionsView(View):
    """View for displaying suggestions to improve AHP matrix consistency"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        # Get matrix and suggestions from session
        matrix_data = request.session.get(f'ahp_matrix_{job_id}')
        suggestions_data = request.session.get(f'ahp_suggestions_{job_id}')
        
        if not matrix_data or not suggestions_data:
            messages.error(request, "No AHP matrix data found. Please try again.")
            return redirect('ahp_matrix', job_id=job.id)
        
        matrix = np.array(matrix_data)
        suggestions = json.loads(suggestions_data)
        
        # Get all criteria for this job
        criteria_list = get_all_criteria(job)
        
        # Convert suggestions to be more user-friendly
        user_suggestions = []
        for key, value in suggestions.get('suggestions', {}).items():
            if key == 'error':
                user_suggestions.append({
                    'message': value,
                    'type': 'error'
                })
                continue
                
            i, j = map(int, key.split(','))
            current_value = matrix[i][j]
            
            # Format the current value nicely
            if current_value < 1:
                current_display = f"1/{int(1/current_value)}" if 1/current_value == int(1/current_value) else f"1/{round(1/current_value, 1)}"
            else:
                current_display = str(int(current_value)) if current_value == int(current_value) else str(round(current_value, 1))
                
            # Format the suggested value nicely
            if value < 1:
                suggested_display = f"1/{int(1/value)}" if 1/value == int(1/value) else f"1/{round(1/value, 1)}"
            else:
                suggested_display = str(int(value)) if value == int(value) else str(round(value, 1))
            
            user_suggestions.append({
                'pair': f"{criteria_list[i][1]} vs {criteria_list[j][1]}",
                'current': current_display,
                'suggested': suggested_display,
                'field_name': f"{criteria_list[i][0]}__{criteria_list[j][0]}"
            })
        
        # Add an option to generate a consistent matrix
        if 'generate_consistent' in request.GET:
            # Generate a consistent matrix using Saaty scale
            criteria_list = get_all_criteria(job)
            priorities, matrix_data = generate_consistent_ahp_matrix(criteria_list)
            
            # Save to session
            request.session[f'consistent_matrix_{job_id}'] = matrix_data
            
            # Calculate consistency ratio to verify
            matrix = np.array(matrix_data)
            cr, is_consistent, _, weights = calculate_consistency_ratio(matrix)
            
            return render(request, 'jobs/ahp_suggestions.html', {
                'job': job,
                'criteria': criteria_list,
                'cr': cr,
                'suggestions': user_suggestions,
                'is_consistent': is_consistent,
                'consistent_matrix_available': True,
                'consistent_cr': cr
            })
        
        return render(request, 'jobs/ahp_suggestions.html', {
            'job': job,
            'criteria': criteria_list,
            'cr': suggestions.get('cr', 0),
            'suggestions': user_suggestions,
            'is_consistent': float(suggestions.get('cr', 1)) < 0.1,
            'consistent_matrix_available': False
        })
    
    def post(self, request, job_id):
        """Handle the case where the user accepts the suggested changes"""
        job = get_object_or_404(Job, id=job_id)
        
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('job_list')
        
        if 'accept_suggestions' in request.POST:
            # User has chosen to accept the suggested changes
            matrix_data = request.session.get(f'ahp_matrix_{job_id}')
            suggestions_data = request.session.get(f'ahp_suggestions_{job_id}')
            
            if not matrix_data or not suggestions_data:
                messages.error(request, "No AHP matrix data found. Please try again.")
                return redirect('ahp_matrix', job_id=job.id)
            
            matrix = np.array(matrix_data)
            suggestions = json.loads(suggestions_data)
            criteria_list = get_all_criteria(job)
            
            # Apply the suggested changes to the matrix
            for key, value in suggestions.get('suggestions', {}).items():
                if key != 'error':
                    i, j = map(int, key.split(','))
                    matrix[i, j] = value
                    matrix[j, i] = 1.0 / value
            
            # Recalculate consistency with the updated matrix
            cr, is_consistent, _, weights = calculate_consistency_ratio(matrix)
            
            # Save the updated matrix to the database
            criteria_keys = [c[0] for c in criteria_list]
            criteria_names = [c[1] for c in criteria_list]
            
            AHPPriority.objects.update_or_create(
                job=job,
                defaults={
                    'matrix_data': matrix.tolist(),
                    'criteria_keys': criteria_keys,
                    'criteria_names': criteria_names,
                    'weights': weights,
                    'consistency_ratio': float(cr),
                    'is_consistent': is_consistent
                }
            )
            
            messages.success(request, f"Suggested changes applied! Your matrix is now {'' if is_consistent else 'more '}consistent (CR = {cr:.4f}).")
            return redirect('job_detail', job_id=job.id)
        
        elif 'accept_consistent_matrix' in request.POST:
            # User has chosen to use the generated consistent matrix
            matrix_data = request.session.get(f'consistent_matrix_{job_id}')
            
            if not matrix_data:
                messages.error(request, "No consistent matrix data found. Please try again.")
                return redirect('ahp_matrix', job_id=job.id)
            
            matrix = np.array(matrix_data)
            criteria_list = get_all_criteria(job)
            
            # Calculate consistency ratio and weights
            cr, is_consistent, _, weights = calculate_consistency_ratio(matrix)
            
            if is_consistent:
                # Save to the AHPPriority model
                criteria_keys = [c[0] for c in criteria_list]
                criteria_names = [c[1] for c in criteria_list]
                
                AHPPriority.objects.update_or_create(
                    job=job,
                    defaults={
                        'matrix_data': matrix.tolist(),
                        'criteria_keys': criteria_keys,
                        'criteria_names': criteria_names,
                        'weights': weights,
                        'consistency_ratio': float(cr),
                        'is_consistent': True
                    }
                )
                
                messages.success(request, f"A consistent matrix has been applied with CR = {cr:.4f}.")
                return redirect('job_detail', job_id=job.id)
            else:
                messages.error(request, "Error: Generated matrix is not consistent. Please try again.")
        
        return redirect('ahp_matrix', job_id=job_id)

# Development/Testing view - restrict to superusers
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class TestAHPMatrixView(View):
    """Debug view to test AHP matrix generation (admin only)"""
    
    def get(self, request):
        # Create some test criteria
        test_criteria = [
            ("c1", "Cost"), 
            ("c2", "Quality"),
            ("c3", "Reliability"),
            ("c4", "Service"),
            ("c5", "Delivery Time")
        ]
        
        # Generate consistent matrix
        weights, matrix = generate_consistent_ahp_matrix(test_criteria)
        
        # Calculate consistency ratio to verify
        matrix_np = np.array(matrix)
        cr, is_consistent, _, _ = calculate_consistency_ratio(matrix_np)
        
        # Format matrix for display
        formatted_matrix = []
        for row in matrix:
            formatted_row = []
            for val in row:
                if val < 1:
                    formatted_val = f"1/{int(1/val)}" if 1/val == int(1/val) else f"1/{round(1/val, 1)}"
                else:
                    formatted_val = str(int(val)) if val == int(val) else str(round(val, 1))
                formatted_row.append(formatted_val)
            formatted_matrix.append(formatted_row)
            
        # Create result dictionary with criterion names
        result = {
            "criteria": [c[1] for c in test_criteria],
            "weights": {test_criteria[i][1]: round(float(weights[i])*100, 2) for i in range(len(test_criteria))},
            "matrix": formatted_matrix,
            "consistency_ratio": round(cr, 4),
            "is_consistent": is_consistent
        }
        
        return JsonResponse(result)

@method_decorator(login_required, name='dispatch')
class ProcessJobApplicationsView(View):
    """View for employers to trigger CV data extraction for a job"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to process applications for this job.")
            return redirect('job_detail', job_id=job_id)
        
        # Get applications count
        application_count = job.applications.count()
        
        # Get already processed applications count
        processed_count = CandidateData.objects.filter(job=job).count()
        
        # Check if any previously processed data exists
        has_processed_data = processed_count > 0
        
        return render(request, 'jobs/process_applications.html', {
            'job': job,
            'application_count': application_count,
            'processed_count': processed_count,
            'has_processed_data': has_processed_data
        })
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to process applications for this job.")
            return redirect('job_detail', job_id=job_id)
        
        # Check if there are any applications
        if job.applications.count() == 0:
            messages.error(request, "This job has no applications to process.")
            return redirect('job_detail', job_id=job_id)
        
        # Check if forced reprocessing is requested
        force_reprocess = request.POST.get('force_reprocess', 'false').lower() == 'true'
        
        # FIX: If force_reprocess is true, we'll proceed with processing regardless of existing data
        if not force_reprocess and CandidateData.objects.filter(job=job).exists():
            messages.info(request, "Applications for this job have already been processed. Use 'Force Reprocess' to process again.")
            return redirect('view_candidate_results', job_id=job_id)
            
        # If we've reached this point, either there's no existing data or we're forcing a reprocess
        # For forced reprocessing, delete previous candidate data to ensure clean processing
        if force_reprocess:
            # Delete existing candidate data for this job
            CandidateData.objects.filter(job=job).delete()
            messages.info(request, "Previous processing data has been cleared. Reprocessing all applications...")
        
        # Trigger the Celery task for processing
        try:
            task = process_job_applications_task.delay(job_id)
            # Store task ID in session for status checking
            request.session[f'process_task_{job_id}'] = task.id
            messages.success(request, "Application processing has been started. This may take a few minutes.")
            return redirect('job_detail', job_id=job_id)
        except Exception as e:
            messages.error(request, f"Error starting processing: {str(e)}")
            return redirect('job_detail', job_id=job_id)

@method_decorator(login_required, name='dispatch')
class CandidateResultsView(View):
    """View for displaying candidate evaluation results"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to view candidate results for this job.")
            return redirect('job_list')
        
        # Get all candidate data for this job
        candidates = CandidateData.objects.filter(job=job).select_related('application__jobseeker').order_by('ahp_rank')
        
        # Check if we have the AHP priority matrix
        has_ahp_priority = hasattr(job, 'ahp_priority')
        
        return render(request, 'jobs/candidate_results.html', {
            'job': job,
            'candidates': candidates,
            'has_ahp_priority': has_ahp_priority
        })


@method_decorator(login_required, name='dispatch')
class ApplicationProcessingStatusView(View):
    """API view for checking application processing status"""
    
    def get(self, request, job_id):
        if not hasattr(request.user, 'employer'):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        job = get_object_or_404(Job, id=job_id)
        if request.user.employer != job.employer:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
            
        # Check if there's a task in the session
        task_id = request.session.get(f'process_task_{job_id}')
        
        if not task_id:
            # No task, check if we have any processed data
            processed_count = CandidateData.objects.filter(job=job).count()
            total_count = job.applications.count()
            
            if processed_count > 0:
                return JsonResponse({
                    'status': 'completed',
                    'processed': processed_count,
                    'total': total_count
                })
            else:
                return JsonResponse({
                    'status': 'not_started',
                    'processed': 0,
                    'total': total_count
                })
        
        # Check task status
        from celery.result import AsyncResult
        result = AsyncResult(task_id)
        
        if result.ready():
            # Task is done, remove from session
            request.session.pop(f'process_task_{job_id}', None)
            
            if result.successful():
                return JsonResponse({
                    'status': 'completed',
                    'result': result.get(),
                    'processed': CandidateData.objects.filter(job=job).count(),
                    'total': job.applications.count()
                })
            else:
                return JsonResponse({
                    'status': 'failed',
                    'error': str(result.result)
                })
        else:
            # Task is still running
            return JsonResponse({
                'status': 'processing',
                'task_id': task_id
            })

@method_decorator(login_required, name='dispatch')
class RankCandidatesAHPView(View):
    """View for ranking candidates using AHP weights"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to rank candidates for this job.")
            return redirect('job_list')
        
        # Check if job has candidates
        candidate_count = CandidateData.objects.filter(job=job).count()
        
        # Check if job has AHP priorities
        has_ahp_priority = hasattr(job, 'ahp_priority')
        
        return render(request, 'jobs/rank_candidates.html', {
            'job': job,
            'candidate_count': candidate_count,
            'has_ahp_priority': has_ahp_priority
        })
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            return JsonResponse({
                'status': 'error',
                'message': "You don't have permission to rank candidates for this job."
            }, status=403)
        
        # Perform the ranking
        result = recalculate_ahp_ranks_for_job(job_id)
        
        if 'error' in result:
            messages.error(request, f"Error ranking candidates: {result['error']}")
            return JsonResponse({
                'status': 'error',
                'message': result['error']
            }, status=400)
        
        messages.success(request, f"Successfully ranked {result['candidates_ranked']} candidates based on AHP weights.")
        return JsonResponse({
            'status': 'success',
            'candidates_ranked': result['candidates_ranked'],
            'redirect_url': request.path
        })

@method_decorator(login_required, name='dispatch')
class GeneticTeamView(View):
    """View for optimizing a team using genetic algorithm"""
    
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to optimize teams for this job.")
            return redirect('job_list')
        
        # Check if job has candidate data
        candidate_count = CandidateData.objects.filter(job=job).count()
        if candidate_count == 0:
            messages.error(request, "No candidate data available. Please process applications first.")
            return redirect('process_applications', job_id=job_id)
            
        # Get the team size from the job or request
        team_size = request.GET.get('team_size', job.nb_places)
        try:
            team_size = int(team_size)
            if team_size <= 0:
                team_size = job.nb_places
        except:
            team_size = job.nb_places
            
        # Check if we can run genetic optimization
        if candidate_count < team_size:
            messages.error(request, f"Not enough candidates ({candidate_count}) for team size ({team_size}). Need at least {team_size} candidates.")
            return redirect('view_candidate_results', job_id=job_id)
            
        # Run the optimization only if requested
        optimized_team = None
        if 'run_optimization' in request.GET:
            optimized_team = optimize_team_for_job(job_id, team_size)
            if 'error' in optimized_team:
                messages.error(request, f"Error in optimization: {optimized_team['error']}")
        print(optimized_team)
        return render(request, 'jobs/genetic_team.html', {
            'job': job,
            'candidate_count': candidate_count,
            'team_size': team_size,
            'optimized_team': optimized_team
        })
        
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to optimize teams for this job.")
            return redirect('job_list')
        
        # Get the requested team size
        try:
            team_size = int(request.POST.get('team_size', job.nb_places))
            if team_size <= 0:
                team_size = job.nb_places
        except:
            team_size = job.nb_places
        
        # Redirect to GET with parameters
        return redirect(f"{request.path}?team_size={team_size}&run_optimization=true")

@method_decorator(login_required, name='dispatch')
class DeleteCriteriaView(View):
    """View for deleting a job criteria"""
    
    def get(self, request, criteria_id):
        criteria = get_object_or_404(Criteria, id=criteria_id)
        job = criteria.job
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to delete criteria for this job.")
            return redirect('job_list')
        
        return render(request, 'jobs/delete_criteria_confirm.html', {
            'criteria': criteria,
            'job': job
        })
    
    def post(self, request, criteria_id):
        criteria = get_object_or_404(Criteria, id=criteria_id)
        job = criteria.job
        job_id = job.id
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to delete criteria for this job.")
            return redirect('job_list')
        
        # Delete the criteria
        criteria_name = criteria.criteria
        criteria.delete()
        
        messages.success(request, f'Criteria "{criteria_name}" has been deleted.')
        
        # If this affects an existing AHP matrix, notify the user
        if hasattr(job, 'ahp_priority'):
            messages.warning(request, "You've deleted a criterion that was part of your priority matrix. Please update your priorities.")
        
        return redirect('add_criteria', job_id=job_id)

# Add this function to update application statuses based on genetic algorithm results
@login_required
def update_application_status(request, job_id):
    """
    Update application statuses based on genetic algorithm team selection.
    Selected team members will have status set to 'selected', others to 'rejected'.
    """
    job = get_object_or_404(Job, pk=job_id)
    
    # Check permissions
    if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
        messages.error(request, "You don't have permission to update applications for this job.")
        return redirect('job_detail', job_id=job_id)
        
    if request.method == 'POST':
        # Get the selected team members from the form
        selected_members = request.POST.get('team_members', '').split(',')
        
        # Filter out empty strings and convert to integers
        selected_member_ids = [int(id) for id in selected_members if id.strip()]
        
        if not selected_member_ids:
            messages.error(request, "No team members were selected. Please run the genetic algorithm first.")
            return redirect('genetic_team', job_id=job_id)
        
        # Get all applications for this job
        applications = Application.objects.filter(job=job)
        selected_count = 0
        rejected_count = 0
        
        # Update statuses based on selection
        with transaction.atomic():
            for app in applications:
                old_status = app.status
                new_status = None
                
                # Check if this jobseeker's application is in the selected team
                if app.jobseeker.id in selected_member_ids:
                    new_status = 'selected'
                    selected_count += 1
                else:
                    new_status = 'rejected'
                    rejected_count += 1
                
                # Only update if status has changed
                if old_status != new_status:
                    app.status = new_status
                    app.save(update_fields=['status'])  # Specify update_fields to fix signal issue
        
        messages.success(
            request, 
            f"Application statuses updated successfully: {selected_count} selected, {rejected_count} rejected."
        )
        
        # Redirect to candidate results page
        return redirect('view_candidate_results', job_id=job_id)
    
    # If not POST, redirect back to genetic team page
    return redirect('genetic_team', job_id=job_id)
