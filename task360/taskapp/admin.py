from django.contrib import admin
from taskapp import models

# Register your models here.
admin.site.register(models.TaskModel)
admin.site.register(models.UserModel)
