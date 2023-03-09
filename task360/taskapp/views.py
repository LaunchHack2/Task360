import secrets
import json
import re
import datetime
import logging

from itertools import islice

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from authenticate.backend import AuthenticateUser

from taskapp.models import UserModel, TaskModel
from taskapp import forms

#from rest_framework.response import Response
#from rest_framework.decorators import api_view

logging.basicConfig(filename='app.log', level=logging.DEBUG)


# Create your views here.
auth = AuthenticateUser(UserModel)




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
                return redirect(reverse('taskapp-account'))

        messages.error(request, 'Invalid Credentials')
        return redirect('taskapp-login')

    
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

            resp.set_cookie('email', form.cleaned_data['email'], max_age=datetime.timedelta(minutes=5), samesite="Lax")
            resp.set_cookie('token', token, max_age=datetime.timedelta(minutes=5), samesite="Lax")

            url = request.build_absolute_uri(f"{reverse('taskapp-setpassword')}?email={form.cleaned_data['email']}&temp_token={token}")

            send_mail(
                subject="Forgot Password",
                message=f"Change Password: {url} \n Access page within the same browser window",
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
        if request.method == "POST":
            form = forms.SetPasswordForm(request.POST)

            if form.is_valid():
                check_password = form.cleaned_data['password'] == form.cleaned_data['confirm_password']

                if check_password: 
                    p = make_password(form.cleaned_data['password'], salt=secrets.token_hex())
                    usr = UserModel.objects.get(pk=request.COOKIES['email'])
                    usr.password = p
                    usr.save()

                messages.success(request, "Password Changed")
                return redirect(reverse('taskapp-login'))

    else:    
        return redirect(reverse('taskapp-forgotpassword'))


    return resp


@auth.is_authenticated(redirect_false='taskapp-login')
def account(request):
    '''
    - Account Page
    - Read Task for specifc user
    '''

    tasks = TaskModel.objects.filter(user=auth.get_user(request.session.get('user_email')))

    return render(request, 'taskapp/account.html', context={'tasks': tasks})


@auth.is_authenticated(redirect_false='taskapp-login')
def create_task(request):
    '''
    - Creates Task
    '''
    form = forms.TaskForm()

    if request.method == "POST":
        task = TaskModel(user=auth.get_user(request.session.get('user_email')))
        form = forms.TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            return redirect(reverse('taskapp-account'))

    return render(request, 'taskapp/create_task.html', context={'form': form})


@auth.is_authenticated(redirect_false='taskapp-login')
def delete_task(request, id): 
    '''
    - Delete Task
    '''
    delete_task = TaskModel.objects.get(pk=id).delete()

    return redirect('taskapp-account')


@auth.is_authenticated(redirect_false='taskapp-login')
def edit_task(request, id): 
    # Possiblity: @api_view['GET']
    # Might make this an api_view function
    '''
    - Edit Task through query parameters
    '''
    task_instance = get_object_or_404(TaskModel, pk=id)

    if request.method == "GET": 
        t = request.GET.get('title')
        desc = request.GET.get('desc', '')

        task_instance.title = t
        task_instance.desc = desc

        task_instance.save()
    

    return redirect('taskapp-account')
