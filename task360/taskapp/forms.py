import secrets

from django import forms
from django.core.validators import validate_email, validate_slug
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

from taskapp.models import RegisterModel


# Custom Validators


# My Forms
class RegisterForm(forms.ModelForm):
    '''
    - Creates a Register Form
    '''
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}), required=True, validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}), required=True, validators=[validate_slug])

    class Meta:
        model = RegisterModel
        fields = '__all__'

    def clean_password(self):
        data = self.cleaned_data['password']

        hashpw = make_password(data, salt=secrets.token_hex(32))

        return hashpw


class LoginForm(forms.Form):
    '''
    - Creates a Login Form
    '''
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}), required=True, validators=[validate_email])
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}), required=True, validators=[validate_slug])


class ForgotPasswordForm(forms.Form):
    '''
    - Creates a Forgot Password Form
    '''
    email = forms.CharField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}), required=True, validators=[validate_email])

    def clean_email(self):
        data = self.cleaned_data['email']

        try:
            check_email = RegisterModel.objects.get(pk=data)
            return data

        except RegisterModel.DoesNotExist:
            raise ValidationError('Email Does Not Exist')


class SetPasswordForm(forms.Form):
    '''
    - Set new password
    '''

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Password"}), required=True, validators=[validate_slug])
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Confirm Password"}), required=True, validators=[validate_slug])



class PostForm(forms.ModelForm):
    '''
    PostForm Object(forms.ModelForm) allows to:
    - Create task
    - Update task
    - Delete task
    '''
    pass
