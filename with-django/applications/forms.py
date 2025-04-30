from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'  # Important for file uploads
        self.helper.add_input(Submit('submit', 'Apply Now', css_class='w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600'))
        
        self.helper.layout = Layout(
            Field('cv', css_class='w-full p-2 border rounded'),
        )
        self.fields['cv'].label = "Upload your CV (PDF)"
        self.fields['cv'].help_text = "Please upload a PDF file of your CV/resume."
        self.fields['cv'].widget.attrs.update({'accept': '.pdf'})