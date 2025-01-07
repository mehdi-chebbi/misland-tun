from django import forms
from ldms.models import LDMSSettings

class LDMSSettingsForm(forms.ModelForm): 
    class Meta:
        model = LDMSSettings
        fields = '__all__' 
