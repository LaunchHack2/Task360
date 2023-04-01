import secrets
import datetime


from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from authenticate.backend import AuthenticateUser

from taskapp.models import UserModel, TaskModel
from taskapp import forms
from taskapp import tasks


from task360.settings import SECRET_KEY


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
    resp = render(request, 'taskapp/login.html', context={'form': form})

    resp.delete_cookie('msg_hash')

    if request.method == "POST":
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            if auth.login(request, email, password):
                auth.generateOTP(pk=email)
                return redirect(reverse('taskapp-mfa'))

        messages.error(request, 'Invalid Credentials')
        return redirect('taskapp-login')

    return resp


@auth.is_authenticated(redirect_true='taskapp-account', mfa=True)
def mfa(request):
    '''
    - Performs MFA (Multi-Factor Authentication)
    '''
    form = forms.MFAForm()

    if request.method == 'POST':
        form = forms.MFAForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data.get('code')
            auth.verifyOTP(request, code)
            tasks.periodic_email.delay(
                topic='Task360 Login',
                msg=f'{request.session.get("user_email")} logged in from {request.session.get("ip_addr")}',
                _from='test@gmail.com',
                to='to@gmail.com'
            )

            return redirect('taskapp-account')

    return render(request, 'taskapp/mfa.html', context={'form': form})


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
            email = form.cleaned_data['email']

            msg = {'email': email, 'token': token, '_hidden_msg': SECRET_KEY}
            hash_msg = auth.hash_msg(msg)

            resp.set_cookie('msg_hash', hash_msg, max_age=datetime.timedelta(
                minutes=5), samesite="Lax")

            url = request.build_absolute_uri(
                f"{reverse('taskapp-setpassword')}?email={email}&temp_token={token}")

            send_mail(
                subject="Forgot Password",
                message=f"Change Password: {url}\n Access page within the same browser window",
                from_email=None,
                recipient_list=[email]
            )

            return resp

    return resp


@auth.is_authenticated(redirect_true='taskapp-account')
def setpassword(request):
    '''
    - Allows user to set password 
    '''

    form = forms.SetPasswordForm()
    resp = render(request, 'taskapp/setpassword.html', context={'form': form})

    verify_msg = auth.verify_hash(
        request.COOKIES.get('msg_hash'),
        auth.hash_msg({'email': request.GET.get('email'),
                      'token': request.GET.get('temp_token'),
                       '_hidden_msg': SECRET_KEY})
    )

    if verify_msg:
        if request.method == "POST":
            form = forms.SetPasswordForm(request.POST)

            if form.is_valid():
                check_password = form.cleaned_data['password'] == form.cleaned_data['confirm_password']

                if check_password:
                    p = make_password(
                        form.cleaned_data['password'], salt=secrets.token_hex())
                    usr = UserModel.objects.get(pk=request.GET.get('email'))
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
    - Edit Task for specifc user via 'API'
    '''
    current_user = auth.get_user(request.session.get('user_email'))
    tasks = TaskModel.objects.filter(user=current_user)

    return render(request, 'taskapp/account.html', context={'tasks': tasks})


@auth.is_authenticated(redirect_false='taskapp-login')
def delete_task(request, id):
    '''
    - Deletes Task
    '''
    delete_task = TaskModel.objects.get(pk=id).delete()

    return redirect('taskapp-account')
