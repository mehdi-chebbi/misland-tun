from django import forms
from communication.models import CommunicationSettings

class CommunicationSettingsForm(forms.ModelForm):
    email_host_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CommunicationSettings
        fields = '__all__'
