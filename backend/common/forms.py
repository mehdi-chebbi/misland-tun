from django import forms
from common.models import CommonSettings

class CommonSettingsForm(forms.ModelForm):
    # email_host_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CommonSettings
        fields = '__all__' 
