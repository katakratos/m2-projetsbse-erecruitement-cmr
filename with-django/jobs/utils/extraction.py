import google.generativeai as genai
import os
import json
import numpy as np
import random
from copy import deepcopy
import pypdf
import matplotlib.pyplot as plt
import time  # Added for rate limiting

# Configure Gemini API (replace with your actual API key)
GOOGLE_API_KEY = "AIzaSyCoGPcEuJifNcE_BqTCZB533P0qizuJ4xk"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.0-pro-exp-02-05"
MODEL_NAME = 'gemini-2.0-flash'
model = genai.GenerativeModel(MODEL_NAME)

def get_pdf_files(folder_path="data"):
    """Get all PDF files in the specified folder."""
    pdf_files = []
    try:
        if os.path.exists(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(folder_path, file))
            print(f"Found {len(pdf_files)} PDF files in {folder_path}")
        else:
            print(f"Error: Folder {folder_path} does not exist")
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
    return pdf_files

def extract_text_from_pdf(pdf_path):
    """Extracts text content from a PDF file."""
    print(f"Extracting text from PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = "".join(page.extract_text() for page in reader.pages)
        print(f"Successfully extracted text from: {pdf_path}")
        return text
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path}")
        return None
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

def evaluate_criteria(resume_data, job=None):
    """
    Evaluate candidate against criteria on a scale of 0-5.
    If job is provided, evaluates based on job-specific criteria.
    """
    # Initialize base criteria dictionary
    criteria = {
        "business_unit_flexibility": 0,  # Ability to work in different business units
        "past_experience": 0,            # Past Experience
        "education_level": 0,            # Level of study
        "language_skills": 0,            # Fluency in a foreign language
        "strategic_thinking": 0,         # Strategic thinking
        "communication_skills": 0,       # Oral communication skills
        "computer_skills": 0,            # Computer skills
        "custom_criteria": {}            # For storing job-specific custom criteria
    }
    
    # C1: Ability to work in different business units (0 = One unit, 5 = Multiple different units)
    experiences = resume_data.get("experience", [])
    companies = set()
    departments = set()
    for exp in experiences:
        if exp.get("company"):
            companies.add(exp.get("company", "").lower())
        # Look for department or business unit info in title or description
        title = exp.get("title", "").lower()
        description = exp.get("description", "").lower()
        # Check for department keywords in title or description
        dept_keywords = ["department", "division", "unit", "team", "sector"]
        for keyword in dept_keywords:
            if keyword in title or keyword in description:
                # Extract potential department names around the keyword
                departments.add(title)  # Simplified approach - using title as department indicator
    
    # Score based on diversity of experience
    if len(companies) > 3 and len(departments) > 2:
        criteria["business_unit_flexibility"] = 5
    elif len(companies) > 2 or len(departments) > 2:
        criteria["business_unit_flexibility"] = 4
    elif len(companies) > 1 or len(departments) > 1:
        criteria["business_unit_flexibility"] = 3
    elif len(companies) == 1 and len(departments) == 1:
        criteria["business_unit_flexibility"] = 2
    elif len(companies) == 1:
        criteria["business_unit_flexibility"] = 1
    
    # C2: Past Experience (0 = <1 year, 1 = 1-3 years, 2 = 3-5 years, 3 = 5-7 years, 4 = 7-10 years, 5 = >10 years)
    years_exp = resume_data.get("number_of_years_experience", "")
    if years_exp:
        try:
            # Try to extract numeric value from the string
            years = 0
            if isinstance(years_exp, str):
                # Remove non-numeric chars except decimal point
                years_exp = ''.join(c for c in years_exp if c.isdigit() or c == '.')
                if years_exp:
                    years = float(years_exp)
            else:
                years = float(years_exp)
            
            # If job is provided, compare candidate's experience with required years
            if job and hasattr(job, 'years_experience_required') and job.years_experience_required > 0:
                job_required_years = job.years_experience_required
                
                # Calculate score based on how candidate's experience compares to requirements
                if years >= job_required_years * 1.5:  # Exceeds requirements by 50% or more
                    criteria["past_experience"] = 5
                elif years >= job_required_years * 1.2:  # Exceeds requirements by 20% or more
                    criteria["past_experience"] = 4
                elif years >= job_required_years:  # Meets requirements
                    criteria["past_experience"] = 3
                elif years >= job_required_years * 0.8:  # Within 20% of requirements
                    criteria["past_experience"] = 2
                elif years >= job_required_years * 0.5:  # At least half the required experience
                    criteria["past_experience"] = 1
            else:
                # Use default scoring if no job-specific requirements
                if years > 10:
                    criteria["past_experience"] = 5
                elif years >= 7:
                    criteria["past_experience"] = 4
                elif years >= 5:
                    criteria["past_experience"] = 3
                elif years >= 3:
                    criteria["past_experience"] = 2
                elif years >= 1:
                    criteria["past_experience"] = 1
                    
        except:
            # If parsing fails, estimate from number of experiences
            num_experiences = len(experiences)
            if num_experiences > 5:
                criteria["past_experience"] = 5
            elif num_experiences > 4:
                criteria["past_experience"] = 4
            elif num_experiences > 3:
                criteria["past_experience"] = 3
            elif num_experiences > 2:
                criteria["past_experience"] = 2
            elif num_experiences > 0:
                criteria["past_experience"] = 1
    
    # C3: Level of study
    education = resume_data.get("education", [])
    highest_degree = 0
    
    # Define education level hierarchy for comparison
    education_levels = {
        'none': 0,
        'high_school': 1,
        'certificate': 2,
        'associates': 3, 
        'bachelors': 4,
        'masters': 5,
        'professional': 6,
        'doctorate': 7
    }
    
    # Map common degree terms to our standardized levels
    degree_mapping = {
        # Doctorate
        'phd': 'doctorate', 'doctorate': 'doctorate', 'doctoral': 'doctorate',
        # Masters
        'master': 'masters', 'mba': 'masters', 'ms ': 'masters', 'ma ': 'masters',
        # Bachelors
        'bachelor': 'bachelors', 'bs ': 'bachelors', 'ba ': 'bachelors', 'bsc': 'bachelors',
        # Associates
        'associate': 'associates', 'diploma': 'associates',
        # Certificate
        'certificate': 'certificate',
        # High School
        'high school': 'high_school', 'secondary': 'high_school'
    }
    
    # Determine candidate's highest education level
    candidate_level = 'none'  # Default if no education found
    for edu in education:
        degree = edu.get("degree", "").lower()
        
        # Map the degree to our standardized levels
        for key, value in degree_mapping.items():
            if key in degree:
                level = value
                # Update if this is a higher level than previously found
                if education_levels.get(level, 0) > education_levels.get(candidate_level, 0):
                    candidate_level = level
    
    # If job is provided, compare education levels
    if job and job.min_education_level:
        job_min_level = job.min_education_level
        candidate_level_value = education_levels.get(candidate_level, 0)
        job_level_value = education_levels.get(job_min_level, 0)
        
        # Score based on how candidate's education compares to requirements
        if candidate_level_value >= job_level_value + 2:  # Far exceeds requirements
            criteria["education_level"] = 5
        elif candidate_level_value >= job_level_value + 1:  # Exceeds requirements
            criteria["education_level"] = 4
        elif candidate_level_value >= job_level_value:  # Meets requirements
            criteria["education_level"] = 3
        elif candidate_level_value >= job_level_value - 1:  # Just below requirements
            criteria["education_level"] = 2
        elif candidate_level_value >= 1:  # Has some education but below requirements
            criteria["education_level"] = 1
    else:
        # Default scoring if no job-specific requirements
        criteria["education_level"] = min(education_levels.get(candidate_level, 0), 5)
    
    # C4: Fluency in a foreign language (0 = None, 1 = Basic, 3 = Fluent, 5 = Bilingual)
    skills = resume_data.get("skills", [])
    summary = resume_data.get("summary", "").lower()
    language_keywords = ["language", "bilingual", "fluent", "proficient", "native", "french", "english", 
                        "spanish", "german", "mandarin", "arabic", "russian", "japanese", "italian"]
    
    language_score = 0
    # Check skills list
    for skill in skills:
        skill_lower = skill.lower()
        for keyword in language_keywords:
            if keyword in skill_lower:
                if "bilingual" in skill_lower or "native" in skill_lower:
                    language_score = 5
                    break
                elif "fluent" in skill_lower or "proficient" in skill_lower:
                    language_score = max(language_score, 3)
                else:
                    language_score = max(language_score, 1)
    
    # Check summary
    if language_score < 5:
        for keyword in language_keywords:
            if keyword in summary:
                if "bilingual" in summary or "native" in summary:
                    language_score = 5
                    break
                elif "fluent" in summary or "proficient" in summary:
                    language_score = max(language_score, 3)
                else:
                    language_score = max(language_score, 1)
    
    criteria["language_skills"] = language_score
    
    # C5: Strategic thinking (0 = None, 5 = Expert with major strategic decisions)
    strategic_keywords = ["strategy", "strategic", "leadership", "vision", "planning", "analysis", 
                         "decision-making", "business development", "growth", "innovation", "transformation"]
    
    strategic_score = 0
    # Check experience descriptions
    strategic_mentions = 0
    for exp in experiences:
        description = exp.get("description", "").lower()
        title = exp.get("title", "").lower()
        
        # Check for strategic positions
        if "director" in title or "executive" in title or "chief" in title or "head" in title or "lead" in title:
            strategic_score = max(strategic_score, 4)
        
        # Count strategic keywords
        for keyword in strategic_keywords:
            if keyword in description or keyword in title:
                strategic_mentions += 1
    
    # Adjust score based on keyword mentions
    if strategic_mentions > 10:
        strategic_score = 5
    elif strategic_mentions > 7:
        strategic_score = max(strategic_score, 4)
    elif strategic_mentions > 5:
        strategic_score = max(strategic_score, 3)
    elif strategic_mentions > 3:
        strategic_score = max(strategic_score, 2)
    elif strategic_mentions > 0:
        strategic_score = max(strategic_score, 1)
    
    criteria["strategic_thinking"] = strategic_score
    
    # C6: Oral communication skills (0 = None, 5 = Expert speaker, confirmed negotiator)
    communication_keywords = ["presentation", "public speaking", "negotiate", "communication", "speaker", 
                             "train", "facilitate", "teach", "lecture", "pitch", "client meeting"]
    
    comm_score = 0
    comm_mentions = 0
    for exp in experiences:
        description = exp.get("description", "").lower()
        title = exp.get("title", "").lower()
        
        # Check for communication-focused roles
        if "presenter" in title or "speaker" in title or "trainer" in title or "teacher" in title or "negotiator" in title:
            comm_score = max(comm_score, 4)
        
        # Count communication keywords
        for keyword in communication_keywords:
            if keyword in description or keyword in title:
                comm_mentions += 1
    
    # Adjust score based on keyword mentions
    if comm_mentions > 8:
        comm_score = 5
    elif comm_mentions > 6:
        comm_score = max(comm_score, 4)
    elif comm_mentions > 4:
        comm_score = max(comm_score, 3)
    elif comm_mentions > 2:
        comm_score = max(comm_score, 2)
    elif comm_mentions > 0:
        comm_score = max(comm_score, 1)
    
    criteria["communication_skills"] = comm_score
    
    # C7: Computer skills (0 = None, 5 = Expert with advanced tools)
    tech_skills = []
    # Extract technology skills from skills list
    for skill in skills:
        skill_lower = skill.lower()
        # Common software/tech terms
        tech_terms = ["software", "programming", "excel", "word", "powerpoint", "sql", "python", "java", 
                     "r", "tableau", "power bi", "sap", "salesforce", "adobe", "microsoft", 
                     "coding", "development", "database", "analysis", "computer"]
        
        for term in tech_terms:
            if term in skill_lower:
                tech_skills.append(skill)
                break
    
    # Score based on number and sophistication of tech skills
    advanced_tech = ["machine learning", "data science", "artificial intelligence", "programming", 
                    "python", "java", "c++", "sql", "r", "development", "blockchain", "cloud"]
    
    basic_tech = ["excel", "word", "powerpoint", "outlook", "microsoft office"]
    
    # If job is provided, get specific skills required for this job
    job_specific_skills = []
    if job and job.skills:
        # Split job skills by comma and clean up each skill
        job_specific_skills = [skill.strip().lower() for skill in job.skills.split(',')]
        
    # Count advanced, basic, and job-specific skills
    advanced_count = sum(1 for skill in tech_skills if any(adv in skill.lower() for adv in advanced_tech))
    basic_count = sum(1 for skill in tech_skills if any(basic in skill.lower() for basic in basic_tech))
    
    # Count job-specific skill matches
    job_skill_matches = 0
    if job_specific_skills:
        # Count how many of the candidate's skills match the job requirements
        job_skill_matches = sum(1 for skill in tech_skills if any(job_skill.lower() in skill.lower() for job_skill in job_specific_skills))
    
    # Adjust scoring to prioritize job-specific skill matches
    if job_specific_skills and job_skill_matches > 0:
        # Calculate match percentage (how many job skills the candidate has)
        match_percentage = job_skill_matches / len(job_specific_skills) if len(job_specific_skills) > 0 else 0
        
        if match_percentage >= 0.8 or job_skill_matches >= 4:
            criteria["computer_skills"] = 5  # Excellent match to job requirements
        elif match_percentage >= 0.6 or job_skill_matches >= 3:
            criteria["computer_skills"] = 4  # Very good match
        elif match_percentage >= 0.4 or job_skill_matches >= 2:
            criteria["computer_skills"] = 3  # Good match
        elif match_percentage > 0:
            criteria["computer_skills"] = 2  # Some match
    else:
        # Fall back to general evaluation if no job specified or no matches
        if advanced_count > 3:
            criteria["computer_skills"] = 5
        elif advanced_count > 1 or (advanced_count > 0 and basic_count > 2):
            criteria["computer_skills"] = 4
        elif advanced_count > 0 or basic_count > 3:
            criteria["computer_skills"] = 3
        elif basic_count > 1:
            criteria["computer_skills"] = 2
        elif basic_count > 0:
            criteria["computer_skills"] = 1
    
    # Scale all criteria values to 0-100 range for consistency with other examples
    # Fix: Only scale numeric criteria, not the custom_criteria dictionary
    for key in criteria:
        if key != "custom_criteria":  # Skip the dictionary field
            criteria[key] = criteria[key] * 20  # Scale from 0-5 to 0-100
    
    # Calculate final score (weighted average)
    base_criteria_count = 7  # The 7 base criteria
    custom_criteria_count = len(criteria.get("custom_criteria", {}))
    total_criteria_count = base_criteria_count + custom_criteria_count
    
    if total_criteria_count > 0:
        # Sum of all base criteria
        base_sum = (
            criteria["business_unit_flexibility"] +
            criteria["past_experience"] +
            criteria["education_level"] +
            criteria["language_skills"] +
            criteria["strategic_thinking"] + 
            criteria["communication_skills"] +
            criteria["computer_skills"]
        )
        
        # Sum of all custom criteria
        custom_sum = sum(criteria.get("custom_criteria", {}).values())
        
        # Weighted final score
        criteria["final_score"] = (base_sum + custom_sum) / total_criteria_count
    else:
        criteria["final_score"] = 0
    
    return criteria

def extract_resume_information(resume_text):
    """Extracts structured information from the resume text using Gemini."""
    print("Calling Gemini API to extract resume information...")

    prompt = f"""
    You are an expert resume parsing assistant. Extract key information from the resume text below and output in JSON format.
    If information isn't explicitly stated, leave the field blank. Return the number of years of experience as a string.
    Estimate experience duration if dates are provided. Include test scores when available.

    Resume text:
    {resume_text}

    Output format:
    {{
        "name": "",
        "email": "",
        "phone_number": "",
        "summary": "",
        "skills": [],
        "number_of_years_experience": "",
        "experience": [{{"title": "", "company": "", "dates": "", "description": ""}}],
        "education": [{{"degree": "", "major": "", "university": "", "graduation_date": ""}}],
        "test_scores": {{"technical_tests": "", "psychometric_tests": ""}},
        "number_of_experiences": 0
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response by removing Markdown delimiters
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:]  # Remove starting ```json
        if json_text.endswith("```"):
            json_text = json_text[:-3]  # Remove ending ```
        json_text = json_text.strip()  # Clean any extra whitespace
        extracted_data = json.loads(json_text)
        
        print("Successfully extracted information from Gemini API.")
        return extracted_data
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}")
        print(f"Raw Response: {response.text}")
        return None
    except Exception as e:
        print(f"General Error: {e}")
        return None

def extract(resume_pdfs: list[str]):
    """Extract candidate information from PDFs and return as a list."""
    candidate_info = []
    for pdf_path in resume_pdfs:
        candidate_name = os.path.splitext(os.path.basename(pdf_path))[0]
        print(f"\nProcessing resume for: {candidate_name}")
        resume_text = extract_text_from_pdf(pdf_path)

        if resume_text:
            extracted_info = extract_resume_information(resume_text)
            if extracted_info:
                try:
                    # Evaluate candidate against criteria
                    criteria_scores = evaluate_criteria(extracted_info)
                    
                    # Add criteria scores to candidate data
                    for key, value in criteria_scores.items():
                        extracted_info[key] = value
                    
                    candidate_info.append(extracted_info)
                except Exception as e:
                    print(f"Error evaluating criteria for {candidate_name}: {e}")
                    # Continue processing other candidates even if this one fails
            else:
                print(f"Could not extract info for {candidate_name}")
        else:
            print(f"Could not read PDF for {candidate_name}")

    return candidate_info

def append_to_json(new_data, filename='candidates.json'):
    """Append new data to existing JSON file or create new file."""
    try:
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    
    existing_data.extend(new_data)
    
    # Sort candidates by final_score in descending order and assign ranks
    sorted_data = sorted(existing_data, key=lambda x: x.get('final_score', 0), reverse=True)
    for i, candidate in enumerate(sorted_data):
        candidate['ahp_rank'] = i + 1
    
    with open(filename, 'w') as f:
        json.dump(sorted_data, f, indent=4)
    print(f"Saved {len(new_data)} candidates to {filename}")

def visualize_candidate_scores(filename='candidates.json'):
    """Generate visualization of candidate scores."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Get top 10 candidates for visualization
        top_candidates = sorted(data, key=lambda x: x.get('final_score', 0), reverse=True)[:10]
        
        # Prepare data for radar chart
        categories = ['Business Units (C1)', 'Experience (C2)', 'Education (C3)', 
                     'Language (C4)', 'Strategic (C5)', 'Communication (C6)', 'Tech Skills (C7)']
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create bar chart for final scores
        names = [c.get('name', f"Candidate {i+1}") for i, c in enumerate(top_candidates)]
        scores = [c.get('final_score', 0) for c in top_candidates]
        
        bars = ax.bar(names, scores, color='skyblue')
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.2f}', ha='center', va='bottom')
        
        ax.set_ylim(0, 100)
        ax.set_ylabel('Final Score')
        ax.set_title('Top 10 Candidates Final Scores')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save the chart
        plt.savefig('candidate_scores.png')
        print("Created visualization: candidate_scores.png")
        
    except Exception as e:
        print(f"Error creating visualization: {e}")

def process_applications_for_job(job_id, batch_size=3, wait_time=20):
    """
    Process all applications for a specific job, extract data from CVs,
    and save the results to the database.
    
    Args:
        job_id: The ID of the job to process applications for
        batch_size: Number of CVs to process at once
        wait_time: Time to wait between batches (seconds)
    
    Returns:
        dict: Summary of processing results
    """
    from django.conf import settings
    from jobs.models import Job, CandidateData
    from applications.models import Application
    from django.db.models import Q  # Import Q for filtering
    import os
    
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return {"error": f"Job with ID {job_id} not found"}
    
    # Get all applications for this job
    applications = Application.objects.filter(job_id=job_id)
    
    if not applications:
        return {"error": f"No applications found for job {job_id}"}
    
    # Get CV file paths
    pdf_files = []
    application_map = {}  # Map file paths to application IDs
    
    for app in applications:
        if app.cv:
            # Get the absolute path to the CV file
            cv_path = os.path.join(settings.MEDIA_ROOT, app.cv.name)
            pdf_files.append(cv_path)
            application_map[cv_path] = app.id
    
    if not pdf_files:
        return {"error": f"No CV files found for job {job_id} applications"}
    
    # Process CVs in batches
    total_batches = (len(pdf_files) + batch_size - 1) // batch_size
    processed_count = 0
    error_count = 0
    
    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"\nProcessing batch {batch_num}/{total_batches} for job {job_id}")
        
        # Extract information from the batch of CVs
        extracted_info_list = extract(batch)
        
        # Process each extracted info and save to database
        for idx, extracted_info in enumerate(extracted_info_list):
            try:
                # Get the application from the mapping
                app_id = application_map.get(batch[idx])
                if not app_id:
                    print(f"Could not find application ID for file {batch[idx]}")
                    error_count += 1
                    continue
                
                # Get the application object
                application = Application.objects.get(id=app_id)
                
                # Check for duplicate names for the same job
                extracted_name = extracted_info.get('name', '').strip().lower()
                if not extracted_name:
                    print(f"Skipping application {app_id} due to missing extracted name.")
                    error_count += 1
                    continue
                
                # Check if a candidate with the same name already exists for this job
                existing_candidate = CandidateData.objects.filter(
                    job=job,
                    name__iexact=extracted_name
                ).first()
                
                if existing_candidate:
                    # Penalize the existing candidate
                    existing_candidate.is_penalize = True
                    existing_candidate.save(update_fields=['is_penalize'])
                    print(f"Penalized existing candidate with name '{extracted_name}' for job {job_id}.")
                    continue  # Skip saving the new candidate
                
                # Evaluate against criteria (using the job object)
                criteria_scores = evaluate_criteria(extracted_info, job)
                
                # Save extracted data to database
                candidate_data, created = CandidateData.objects.update_or_create(
                    application=application,
                    job=job,
                    defaults={
                        'jobseeker': application.jobseeker,  # Add the jobseeker reference
                        'raw_data': extracted_info,
                        'name': extracted_name,
                        'email': extracted_info.get('email', ''),
                        'years_experience': extracted_info.get('number_of_years_experience', ''),
                        'business_unit_flexibility': criteria_scores.get('business_unit_flexibility', 0),
                        'past_experience': criteria_scores.get('past_experience', 0),
                        'education_level': criteria_scores.get('education_level', 0),
                        'language_skills': criteria_scores.get('language_skills', 0),
                        'strategic_thinking': criteria_scores.get('strategic_thinking', 0),
                        'communication_skills': criteria_scores.get('communication_skills', 0),
                        'computer_skills': criteria_scores.get('computer_skills', 0),
                        'custom_criteria_scores': criteria_scores.get('custom_criteria', {}),
                        'final_score': criteria_scores.get('final_score', 0),
                        'is_penalize': False,  # New candidate is not penalized
                    }
                )
                
                processed_count += 1
                print(f"Successfully processed application {app_id}, score: {criteria_scores.get('final_score', 0)}")
                
            except Exception as e:
                print(f"Error processing extracted info at index {idx}: {e}")
                error_count += 1
        
        # Wait before processing next batch if not the last batch
        if i + batch_size < len(pdf_files):
            print(f"Waiting {wait_time} seconds before next batch...")
            time.sleep(wait_time)
    
    # Update rankings after all processing is complete
    update_candidate_rankings(job_id)
    
    return {
        "job_id": job_id,
        "total_applications": len(pdf_files),
        "processed": processed_count,
        "errors": error_count
    }

def update_candidate_rankings(job_id):
    """Update AHP rankings for all candidates of a job"""
    from jobs.models import CandidateData
    
    # Get all candidate data for this job, ordered by final score
    candidates = CandidateData.objects.filter(job_id=job_id).order_by('-final_score')
    
    # Update ranking
    for i, candidate in enumerate(candidates):
        candidate.ahp_rank = i + 1
        candidate.save(update_fields=['ahp_rank'])
    
    return len(candidates)

if __name__ == "__main__":
    folder_path = "data"
    batch_size = 3
    wait_time = 60  # seconds between batches

    pdf_files = get_pdf_files(folder_path)
    total_batches = (len(pdf_files) + batch_size - 1) // batch_size

    for i in range(0, len(pdf_files), batch_size):
        batch = pdf_files[i:i+batch_size]
        batch_num = i//batch_size + 1
        print(f"\nProcessing batch {batch_num}/{total_batches}")
        
        candidates = extract(batch)
        append_to_json(candidates)
        
        if i + batch_size < len(pdf_files):
            print(f"Waiting {wait_time/60} minutes before next batch...")
            time.sleep(wait_time)

    print("\nAll batches processed. Final data saved to candidates.json")
    
    # Generate visualization of candidate scores
    visualize_candidate_scores()