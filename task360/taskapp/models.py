import uuid

from django.db import models

# Create your models here.


class UserModel(models.Model):
    email = models.EmailField(max_length=200, primary_key=True, unique=True)
    password = models.CharField(max_length=200)


class TaskModel(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
    )
    user = models.ForeignKey(
        UserModel, 
        on_delete=models.CASCADE, 
        related_name="user", 
        null=True, 
        blank=True,
       )
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['complete']


class OTPModel(models.Model): 
    key = models.CharField(max_length=32, unique=True, blank=True, null=True)
    url = models.URLField(unique=True, blank=True, null=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='otp_user')