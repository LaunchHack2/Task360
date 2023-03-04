from django.urls import path
from taskapp import views

# Paths can be changed, just creating something for a visual

urlpatterns = [
    path('', views.register, name='taskapp-register'),
    path('login', views.login, name='taskapp-login'), 
    path('logout', views.logout, name='taskapp-logout'),
    path('forgotpassword', views.forgotpassword, name='taskapp-forgotpassword'), 
    path('setpassword', views.setpassword, name='taskapp-setpassword'),
    path('account', views.account, name='taskapp-account'),
]
