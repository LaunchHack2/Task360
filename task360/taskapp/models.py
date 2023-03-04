from django.db import models

# Create your models here.


class RegisterModel(models.Model):
    '''
    - Stores users email and password
    '''
    email = models.EmailField(max_length=200, primary_key=True)
    password = models.CharField(max_length=200)



class PostModel(models.Model):
    '''
    - Stores New Task
    - Relationship with RegisterModel 
    - Allows you to know what user created what post
    '''
    task = models.CharField(max_length=100, default="Some Task")
    user = models.ForeignKey(RegisterModel, on_delete=models.CASCADE, related_name='user', default="Some User")

