from django.urls import path, re_path
from taskapp import views

# Paths can be changed, just creating something for a visual

urlpatterns = [
    path('', views.register, name='taskapp-register'),
    path('login', views.login, name='taskapp-login'), 
    path('logout', views.logout, name='taskapp-logout'),
    path('forgotpassword', views.forgotpassword, name='taskapp-forgotpassword'), 
    path('setpassword', views.setpassword, name='taskapp-setpassword'),
    path('myaccount', views.account, name='taskapp-account'),
    path('myaccount/create_task/', views.create_task, name='taskapp-createtask'),
    path('myaccount/delete_task/<uuid:id>', views.delete_task, name="taskapp-deletetask"),
    path('myaccount/edit_task/<uuid:id>', views.edit_task, name='taskapp-edit_task'), 
]
