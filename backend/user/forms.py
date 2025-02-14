from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from user.models import CustomUser, UserSettings

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # del self.fields['username'] #delete username field

    class Meta:
        model = CustomUser
        fields = ("email", )

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(CustomUserChangeForm, self).__init__(*args, **kargs)
        # del self.fields['username']

    class Meta:
        model = CustomUser
        fields = ("email", )

class UserSettingsForm(forms.ModelForm):
    # email_host_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserSettings
        fields = '__all__' # ('name', 'email', 'password', 'instrument_purchase', 'house_no', 'address_line1', 'address_line2', 'telephone', 'zip_code', 'state', 'country')
