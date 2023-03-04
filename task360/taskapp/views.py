import secrets
import json
import re

from itertools import islice

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from authenticate.backend import AuthenticateUser

from taskapp.models import RegisterModel, PostModel
from taskapp import forms

from rest_framework.response import Response
from rest_framework.decorators import api_view


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
    resp =  render(request, 'taskapp/login.html', context={'form': form})


    resp.delete_cookie('token')
    resp.delete_cookie('email')

    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            if auth.login(request, email, password):
                messages.success(request, 'Successfully Logged In')
                return redirect(reverse('taskapp-login'))

            messages.error(request, 'Invalid Credentials')

    
    return resp 

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
    resp = render(request, 'taskapp/forgotpassword.html',
                  context={'form': form})


    if request.method == "POST":
        
        form = forms.ForgotPasswordForm(request.POST)

        if form.is_valid():
            token = secrets.token_urlsafe(32)           

            resp.set_cookie('email', form.cleaned_data['email'])
            resp.set_cookie('token', token)

            url = request.build_absolute_uri(f"{reverse('taskapp-setpassword')}?email={form.cleaned_data['email']}&temp_token={token}")

            send_mail(
                subject="Forgot Password",
                message=f"Change Password: {url}",
                from_email=None,
                recipient_list=[form.cleaned_data['email']]
            )

            return resp

    return resp


@auth.is_authenticated(redirect_true='taskapp-account')
def setpassword(request):
    '''
    - Allows user to set password 
    '''

    form = forms.SetPasswordForm()
    resp = render(request, 'taskapp/setpassword.html', context={'form': form })

    check_token = request.GET.get('temp_token') == request.COOKIES.get('token')
    check_email = request.GET.get('email') == request.COOKIES.get('email')

    if check_token and check_email:
        pass
    else:    
        return redirect(reverse('taskapp-forgotpassword'))

    if request.method == "POST":
        form = forms.SetPasswordForm(request.POST)

        if form.is_valid():
            check_password = form.cleaned_data['password'] == form.cleaned_data['confirm_password']

            if check_password: 
                p = make_password(form.cleaned_data['password'], salt=secrets.token_hex())
                usr = RegisterModel.objects.get(pk=request.COOKIES['email'])
                usr.password = p
                usr.save()

            return redirect(reverse('taskapp-login'))

    return resp



@auth.is_authenticated(redirect_false='taskapp-login')
def account(request):
    '''
    - Account Page
    - Task will be created on this page
    - Store task
    '''

    return render(request, 'taskapp/account.html')



# Using cookies to store task

#    batch_size = 100
#
#    objs = map(lambda t: PostModel(task=t, user=current_user), content)
#
#    while True:
#        batch = list(islice(objs, batch_size))
#        if not batch:
#            break
#        PostModel.objects.bulk_create(batch, batch_size, ignore_conflicts=True)
#
    