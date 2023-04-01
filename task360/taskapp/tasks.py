import time

from celery import shared_task
from django.core.mail import send_mail



@shared_task()
def periodic_email(topic:str, msg:str, _from:str, to:str) -> None:

    send_mail(
        subject=topic,
        message=msg, 
        from_email=_from, 
        recipient_list=[to]
    )

    time.sleep(1)
    return "Email sent"


@shared_task
def create_new_task(taskmodel_obj, data):
    taskmodel_obj.title = data['title']
    taskmodel_obj.description = data['description']
    taskmodel_obj.notify = data['notify']
