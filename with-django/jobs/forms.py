from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import Job, Criteria
import numpy as np

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'nb_places', 'location', 'type', 
            'experience', 'years_experience_required', 'salary', 'deadline', 
            'requirements', 'skills', 'remote_work',
            'business_unit_flexibility', 'past_experience_required', 
            'min_education_level', 'foreign_language_required', 
            'strategic_thinking_required', 'oral_communication_required',
            'computer_skills_required'
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'years_experience_required': 'Enter the number of years of experience required for this job',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Job', css_class='w-full py-2 px-4 bg-green-500 text-white rounded hover:bg-green-600'))
        
        self.helper.layout = Layout(
            Div(
                Field('title', css_class='w-full p-2 border rounded'),
                Field('description', css_class='w-full p-2 border rounded'),
                css_class='space-y-3'
            ),
            Row(
                Column('nb_places', css_class='w-full md:w-1/3 px-2'),
                Column('location', css_class='w-full md:w-1/3 px-2'),
                Column('type', css_class='w-full md:w-1/3 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('experience', css_class='w-full md:w-1/3 px-2'),
                Column('years_experience_required', css_class='w-full md:w-1/3 px-2'),
                Column('salary', css_class='w-full md:w-1/3 px-2'),
                Column('deadline', css_class='w-full md:w-1/3 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Field('requirements', css_class='w-full p-2 border rounded'),
            Field('skills', css_class='w-full p-2 border rounded'),
            Field('remote_work', css_class='w-full p-2 border rounded'),
            HTML("<h3 class='text-lg font-semibold mt-4 mb-3'>Job Criteria</h3>"),
            Div(
                Div(
                    Div(Field('business_unit_flexibility'), css_class='w-1/2 md:w-1/4 px-3'),
                    Div(Field('past_experience_required'), css_class='w-1/2 md:w-1/4 px-3'),
                    Div(Field('foreign_language_required'), css_class='w-1/2 md:w-1/4 px-3'),
                    Div(Field('strategic_thinking_required'), css_class='w-1/2 md:w-1/4 px-3'),
                    css_class='flex flex-wrap -mx-3'
                ),
                Div(
                    Div(Field('oral_communication_required'), css_class='w-1/2 md:w-1/3 px-3'),
                    Div(Field('computer_skills_required'), css_class='w-1/2 md:w-1/3 px-3'),
                    Div(Field('min_education_level', css_class='w-full p-2 border rounded'), css_class='w-full md:w-1/3 px-3'),
                    css_class='flex flex-wrap -mx-3 mt-3'
                ),
                css_class='mb-4 flex-row'
            ),
        )

class CriteriaForm(forms.Form):
    multiple_criteria = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'class': 'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
                'placeholder': 'Enter your criteria here...'
            }
        ),
        label="Job Criteria",
        help_text="Enter one criterion per line. Each line will be added as a separate criterion."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'
        
        # Shadcn-styled submit button
        self.helper.add_input(
            Submit(
                'submit', 
                'Add Criteria', 
                css_class='inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2'
            )
        )
        
        # Improve label styling
        self.helper.layout = Layout(
            Div(
                HTML('<label for="id_multiple_criteria" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Job Criteria</label>'),
                Field('multiple_criteria', css_class='mt-2'),
                HTML('<p class="text-sm text-muted-foreground mt-1">Enter one criterion per line. Each line will be added as a separate criterion.</p>'),
                css_class='space-y-2'
            )
        )

class AHPMatrixForm(forms.Form):
    """
    Dynamic form for AHP pairwise comparison matrix
    The form fields are dynamically generated based on the criteria
    """
    
    def __init__(self, criteria_list, *args, **kwargs):
        """
        Initialize form with dynamic fields based on criteria
        
        Args:
            criteria_list: List of (id, name) tuples for all criteria
        """
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = 'post'
        
        # Add explanatory text
        scale_info = HTML("""
            <div class="mb-6 bg-blue-50 p-4 rounded">
                <h3 class="text-lg font-medium text-blue-800">AHP Preference Scale</h3>
                <p class="text-sm text-blue-600 mb-2">Use the following scale to compare criteria:</p>
                <ul class="text-sm text-blue-600 list-disc pl-5">
                    <li>1: Equal importance</li>
                    <li>3: Moderate importance</li>
                    <li>5: Strong importance</li>
                    <li>7: Very strong importance</li>
                    <li>9: Extreme importance</li>
                    <li>2, 4, 6, 8: Intermediate values</li>
                </ul>
            </div>
        """)
        
        # Store criteria for future reference
        self.criteria = criteria_list
        
        # Create a field for each comparison
        for i, (id_i, name_i) in enumerate(criteria_list):
            for j, (id_j, name_j) in enumerate(criteria_list):
                if i < j:  # Only create fields for upper triangle
                    field_name = f"{id_i}__{id_j}"
                    self.fields[field_name] = forms.ChoiceField(
                        choices=[
                            ('1', '1'),
                            ('2', '2'),
                            ('3', '3'),
                            ('4', '4'),
                            ('5', '5'),
                            ('6', '6'),
                            ('7', '7'),
                            ('8', '8'),
                            ('9', '9'),
                            ('1/2', '1/2'),
                            ('1/3', '1/3'),
                            ('1/4', '1/4'),
                            ('1/5', '1/5'),
                            ('1/6', '1/6'),
                            ('1/7', '1/7'),
                            ('1/8', '1/8'),
                            ('1/9', '1/9'),
                        ],
                        label=f"{name_i} vs {name_j}",
                        required=True,
                        initial='1'
                    )
    
    def get_matrix(self):
        """
        Convert form data to a numpy matrix
        
        Returns:
            numpy.ndarray: The pairwise comparison matrix
        """
        n = len(self.criteria)
        matrix = np.ones((n, n))  # Initialize with 1s (diagonal values)
        
        for i, (id_i, _) in enumerate(self.criteria):
            for j, (id_j, _) in enumerate(self.criteria):
                if i < j:
                    field_name = f"{id_i}__{id_j}"
                    value_str = self.cleaned_data.get(field_name, '1')
                    
                    # Debug print to verify values are being processed
                    print(f"Processing field {field_name}: value = {value_str}")
                    
                    # Parse the value (handles fractions like 1/3)
                    if '/' in value_str:
                        num, denom = value_str.split('/')
                        value = float(num) / float(denom)
                    else:
                        value = float(value_str)
                        
                    matrix[i, j] = value
                    matrix[j, i] = 1.0 / value
        
        # Debug print the entire matrix
        print("Final Matrix:")
        print(matrix)
                    
        return matrix
