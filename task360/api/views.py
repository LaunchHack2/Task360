import json

from taskapp.models import TaskModel, UserModel
from authenticate.backend import AuthenticateUser

from rest_framework.decorators import api_view
from rest_framework.response import Response

from taskapp import tasks

auth = AuthenticateUser(UserModel)

@auth.is_authenticated(redirect_false='taskapp-login')
@api_view(['POST', 'GET'])
def create_edit_task(request):
    '''
    - Creates Task via api 
    - Edit Task via api
    '''

    edit_id = request.GET.get('task_id', None)
    data = json.loads(request.data)
    user = request.session.get('user_email')

    if not edit_id:
        task = TaskModel(user=auth.get_user(user))
        task.title = data['title'].replace('\n', '')
        task.description = data['description']
        task.period = data['period']
        task.notify = int(data['notify'])
        task.status = data['status']
        task.save()
    else: 
        task = TaskModel.objects.get(pk=edit_id)
        task.edited = True
        task.title = data['title'].replace('\n', '')
        task.description = data['description']
        task.period = data['period']
        task.status = data['status']
        task.notify = int(data['notify'])
        task.save()

    return Response({'data': 'completed'})

