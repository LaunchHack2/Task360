import uuid
import secrets
import json

from datetime import datetime, timedelta

from django.db import models
from django_celery_beat.models import IntervalSchedule
from django.db.models import signals
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask



# Create your models here.


class UserModel(models.Model):
    '''
    - Creates a user
    '''
    email = models.EmailField(max_length=200, primary_key=True, unique=True)
    password = models.CharField(max_length=200)


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
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)
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


#class TrackTaskChanges(models.Model): 
#    '''
#    - Track Changes Across Tasks
#    - For now, only tracks task status
#    '''
#    task = models.OneToOneField(TaskModel, on_delete=models.CASCADE, related_name='task', blank=True, null=True)
#    original_status = models.CharField(default="Notdone", max_length=20)
#    updated_status = models.CharField(default="Notdone", max_length=20)
#    status_state = models.BooleanField(default=False)
#
#    def clean(self) -> None: 
#        if self.original_status == self.updated_status: 
#            self.status_state = False
#        else: 
#            self.status_state = True


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
                MyPeriodicTask.objects.get(task_model_uuid=instance.id).delete()
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


@receiver(signals.pre_save, sender=TaskModel)
def pre_task_pending(sender, instance, signal, *args, **kwargs):
    pass
