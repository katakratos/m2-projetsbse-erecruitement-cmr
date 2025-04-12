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
        self.fields['username'].label = "Email or Username"
        
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
