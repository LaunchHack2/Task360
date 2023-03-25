from django.contrib import admin
from taskapp import models
from django_celery_beat.admin import PeriodicTaskAdmin, PeriodicTaskForm

class MyPeriodicTaskForm(PeriodicTaskForm):
    class Meta: 
        model = models.MyPeriodicTask
        exclude = ()

class MyPeriodicTaskAdmin(PeriodicTaskAdmin): 
    form = MyPeriodicTaskForm
    model = models.MyPeriodicTask


# Register your models here.
admin.site.register(models.TaskModel)
admin.site.register(models.UserModel)
admin.site.register(models.OTPModel)
admin.site.register(models.MyPeriodicTask, MyPeriodicTaskAdmin)
