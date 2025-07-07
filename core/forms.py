from django import forms
from .models import ScanResult

class ScanUploadForm(forms.ModelForm):
    class Meta:
        model = ScanResult
        fields = ['image']



