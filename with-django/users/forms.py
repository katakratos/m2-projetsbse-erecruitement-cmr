from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import User, JobSeeker, Employer

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Login', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            Field('username', css_class='w-full p-2 border rounded'),
            Field('password', css_class='w-full p-2 border rounded'),
        )
        self.fields['username'].label = "Username"
        
class JobSeekerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = JobSeeker
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='w-full md:w-1/2 px-2'),
                Column('last_name', css_class='w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            'username',
            'email',
            'phone_number',
            'password1',
            'password2',
        )

class EmployerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Employer
        fields = ('username', 'email', 'password1', 'password2', 'company_name', 'company_description', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            'username',
            'email',
            'company_name',
            'company_description',
            'phone_number',
            'password1',
            'password2',
        )

class JobSeekerProfileUpdateForm(forms.ModelForm):
    """Form for JobSeekers to update their profile information"""
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = JobSeeker
        fields = ('first_name', 'last_name', 'email', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Profile', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='w-full md:w-1/2 px-2'),
                Column('last_name', css_class='w-full md:w-1/2 px-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            'email',
            'phone_number',
        )

class EmployerProfileUpdateForm(forms.ModelForm):
    """Form for Employers to update their profile information"""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    company_name = forms.CharField(max_length=100, required=False)
    company_description = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = Employer
        fields = ('email', 'phone_number', 'company_name', 'company_description')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Profile', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            'email',
            'phone_number',
            'company_name',
            'company_description',
        )

class PasswordChangeCustomForm(forms.Form):
    """Form for users to change their password"""
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Change Password', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        self.helper.layout = Layout(
            'current_password',
            'new_password',
            'confirm_password',
        )
