from django.urls import path, re_path
from taskapp import views
from api import views as api_views

# Paths can be changed, just creating something for a visual

urlpatterns = [
    path('', views.register, name='taskapp-register'),
    path('login', views.login, name='taskapp-login'), 
    path('login/mfa', views.mfa, name='taskapp-mfa'),
    path('logout', views.logout, name='taskapp-logout'),
    path('forgotpassword', views.forgotpassword, name='taskapp-forgotpassword'), 
    path('setpassword', views.setpassword, name='taskapp-setpassword'),
    path('myaccount', views.account, name='taskapp-account'),
    path('myaccount/create_task', api_views.create_edit_task, name='taskapp-createtask'),
    path('myaccount/delete_task/<uuid:id>', views.delete_task, name="taskapp-deletetask"),
    path('myaccount/create_group', views.create_group, name='taskapp-creategroup'), 
    path('myaccount/show_tasks/<uuid:id>', api_views.show_task_in_grp, name='taskapp-showtasks'),
    path('myaccount/show_members/<uuid:id>', api_views.show_grp_members, name="taskapp-members"), 
    path('myaccount/add_member/<uuid:id>', api_views.add_members, name="taskapp-addmembers")
]
