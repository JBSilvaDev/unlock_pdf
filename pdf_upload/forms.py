from django import forms
from .models import PDFFile

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.pdf',
                'required': True
            }),
        }