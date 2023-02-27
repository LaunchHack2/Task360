import secrets
import asyncio

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

from authenticate.backend import AuthenticateUser

from taskapp.models import RegisterModel
from taskapp import forms


# Create your views here.
auth = AuthenticateUser(RegisterModel)


@auth.is_authenticated(redirect_true='taskapp-account')
def register(request):
    '''
    - Register Page
    '''
    form = forms.RegisterForm()

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Succesfully Registered")
            return redirect(reverse('taskapp-login'))

    return render(request, 'taskapp/register.html', context={'form': form})


@auth.is_authenticated(redirect_true='taskapp-account')
def login(request):
    '''
    - Login Page
    '''
    form = forms.LoginForm()

    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            if auth.login(request, email, password):
                messages.success(request, 'Successfully Logged In')
                return redirect(reverse('taskapp-login'))

            messages.error(request, 'Invalid Credentials')

    return render(request, 'taskapp/login.html', context={'form': form})


@auth.is_authenticated(redirect_false='taskapp-login')
def logout(request):
    '''
    - Logout Users
    '''
    if request.method == "GET":
        auth.logout(request)
        messages.success(request, 'Sucessfully Logged out')
        return redirect(reverse('taskapp-login'))


@auth.is_authenticated(redirect_true='taskapp-account')
def forgotpassword(request):
    '''
    - Forgot Password Page
    '''
    form = forms.ForgotPasswordForm()

    if request.method == "POST":
        form = forms.ForgotPasswordForm(request.POST)

        if form.is_valid():
            token = secrets.token_urlsafe(32)
            url = ''

            return redirect(reverse('taskapp-login'))

    return render(request, 'taksapp/forgotpassword.html', context={'form': form})


#For me to remember: 
#Possibly thinking about using the session to store task
#and grabbing the task from the session to then store it in the PostModel database

@auth.is_authenticated(redirect_false='taskapp-login')
def account(request): 
    '''
    - Account Page
    - Task will be created on this page
    - Store task in user session
    '''

    return render(request, 'taskapp/account.html') 
