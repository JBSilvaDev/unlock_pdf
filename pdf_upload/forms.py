from django import forms
from .models import PDFFile

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ('file',)
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.pdf'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError("Apenas arquivos PDF são permitidos.")
        return file