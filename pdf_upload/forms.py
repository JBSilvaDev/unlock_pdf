from django import forms
from .models import PDFFile

class PDFUploadForm(forms.ModelForm):
    digits = forms.IntegerField(
        label='Número de dígitos da senha',
        min_value=1,
        max_value=6,
        initial=4,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o número de dígitos (1-6)'
        })
    )
    
    class Meta:
        model = PDFFile
        fields = ('file', 'digits')
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.pdf',
                'class': 'form-control'
            }),
        }
    
    def clean_digits(self):
        digits = self.cleaned_data.get('digits')
        if digits and (digits < 1 or digits > 6):
            raise forms.ValidationError("O número de dígitos deve estar entre 1 e 6.")
        return digits