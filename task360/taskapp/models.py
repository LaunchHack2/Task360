import uuid
import secrets
import json

from datetime import datetime, timedelta

from django.db import models
from django_celery_beat.models import IntervalSchedule
from django.db.models import signals
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from rest_framework import serializers


# Create your models here.


class UserModel(models.Model):
    '''
    - Represents a user
    '''
    username = models.CharField(
        max_length=100, null=True, blank=True, unique=True)
    email = models.EmailField(max_length=200, primary_key=True, unique=True)
    password = models.CharField(max_length=200)

    def __repr__(self):
        return self.username


class GroupModel(models.Model):
    '''
    - Represents a Group
    - Users and Tasks can be added to group
    '''
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    groupowner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="owner",
        null=True,
        blank=True
    )
    groupname = models.CharField(max_length=100)
    groupusers = models.ManyToManyField(UserModel)
    grouptasks = models.ManyToManyField("TaskModel")

    def __repr__(self) -> str:
        return self.groupname

class GroupModelSerializer(serializers.ModelSerializer):
    class Meta: 
        model = GroupModel
        fields = ['groupusers']


class TaskModel(models.Model):
    '''
    - Stores user tasks
    '''

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

    group = models.ForeignKey(
        GroupModel,
        on_delete=models.CASCADE,
        related_name="group",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200, null=True)
    description = models.TextField(default="None", null=True, blank=True)
    complete = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    notify = models.PositiveIntegerField(blank=True, null=True)
    edited = models.BooleanField(default=False)

    period = models.CharField(
        max_length=12,
        choices=IntervalSchedule.PERIOD_CHOICES[:-1],
        blank=True,
        null=True,
    )

    status_choices = (
        ("Notdone", "not done"),
        ("Completed", "complete"),
        ("Inprocess", "inprocess"),
    )

    status = models.CharField(
        max_length=12,
        choices=status_choices,
        default="Notdone"
    )

    class Meta:
        ordering = ['complete']


class TaskModelSerialzer(serializers.ModelSerializer):
    class Meta: 
        model = TaskModel
        fields = ['status', 'period', 'notify', 'description', 'title', 'group', 'id']


class MainGoalModel(models.Model):
    pass


class OTPModel(models.Model):
    '''
    - OTP, One-Time Password Model
    - Uses Google Authenticator App
    - Stores users key in database
    '''
    key = models.CharField(max_length=32, unique=True, blank=True, null=True)
    url = models.URLField(unique=True, blank=True, null=True)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name='otp_user')


class MyPeriodicTask(PeriodicTask):
    '''
    - Customized Periodic Task
    - Adds the task_model and task_model_uuid to periodic task 
    - By adding these, I can remove or disable specifc periodic task
    by task model and id
    '''

    task_model = models.ForeignKey(
        TaskModel,
        on_delete=models.CASCADE,
        related_name='task_model',
        verbose_name='taskmodel.task',
        null=True,
        db_constraint=False,
    )

    task_model_uuid = models.UUIDField(null=True, blank=True)


def check_time(func):
    def wrapfunc(*args, **kwargs):

        instance = kwargs['instance']
        time = None

        if instance.period == "minutes":
            time = IntervalSchedule.MINUTES
        elif instance.period == "hours":
            time = IntervalSchedule.HOURS
        elif instance.period == "days":
            time = IntervalSchedule.DAYS
        elif instance.period == "seconds":
            time = IntervalSchedule.SECONDS
        else:
            time = None

        if time != None:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=instance.notify,
                period=time
            )
            return func(*args, **kwargs, sched=schedule)
        else:
            return func(*args, **kwargs, time=time)
    return wrapfunc


@receiver(signals.post_save, sender=TaskModel)
@check_time
def post_save_email(sender, instance, signal, *args, **kwargs):
    '''
        - Checks if the task has been edited
        - If edited, create a new notification for the user
    '''

    task_name = f"{secrets.randbits(32)}task"

    if instance.edited:
        if instance.status == 'Completed':
            try:
                MyPeriodicTask.objects.get(
                    task_model_uuid=instance.id).delete()
            except:
                pass

        else:
            MyPeriodicTask.objects.create(
                interval=kwargs['sched'],
                name=task_name,
                task_model_uuid=instance.id,
                task='taskapp.tasks.periodic_email',
                kwargs=json.dumps({
                    'topic': f"Notification for: {instance.title}",
                    "msg": instance.description,
                    "_from": 'test@gmail.com',
                    'to': 'to@gmail.com'
                }),
                one_off=True,
                enabled=True,
                expires=datetime.utcnow() + timedelta(minutes=15)
            )

    else:
        MyPeriodicTask.objects.create(
            interval=kwargs['sched'],
            name=task_name,
            task_model_uuid=instance.id,
            task='taskapp.tasks.periodic_email',
            kwargs=json.dumps({
                'topic': f"Notification for: {instance.title}",
                "msg": instance.description,
                "_from": 'test@gmail.com',
                'to': 'to@gmail.com'
            }),
            one_off=True,
            enabled=True,
            expires=datetime.utcnow() + timedelta(minutes=15)
        )
