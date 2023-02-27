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
    '''
    pass


class TempKeyModel(models.Model):
    '''
    - TempKey Model stores temporary tokens for forgotten passwords
    ''' 
    pass