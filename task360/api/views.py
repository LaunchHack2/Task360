import json

from taskapp import models
from authenticate.backend import AuthenticateUser

from rest_framework.decorators import api_view
from rest_framework.response import Response


auth = AuthenticateUser(models.UserModel)

@auth.is_authenticated(redirect_false='taskapp-login')
@api_view(['POST'])
def create_edit_task(request):
    '''
    - Creates Task via api 
    - Edit Task via api
    '''

    edit_id = request.GET.get('task_id', None)
    data = json.loads(request.data)
    user = request.session.get('user_email')

    if not edit_id:
        task = models.TaskModel(user=auth.get_user(user))
        grp = models.GroupModel.objects.get(id=data['group_id'])

        task.title = data['title'].replace('\n', '')
        task.description = data['description']
        task.period = data['period']
        task.notify = int(data['notify'])
        task.status = data['status']
        task.group = grp
        task.save()

        
        grp.grouptasks.add(task)

    else: 
        task = models.TaskModel.objects.get(pk=edit_id)
        task.edited = True
        task.title = data['title'].replace('\n', '')
        task.description = data['description']
        task.period = data['period']
        task.status = data['status']
        task.notify = int(data['notify'])
        task.save()

    return Response({'data': 'completed'})


@auth.is_authenticated(redirect_false='taskapp-login')
@api_view(["GET"])
def show_task_in_grp(request, id): 
    user = request.session.get('user_email')
    
    tasks_in_grp = models.TaskModel.objects.filter(user=auth.get_user(user), group=id).all()
    serialize = models.TaskModelSerialzer(tasks_in_grp, many=True)

    return Response(serialize.data)


@auth.is_authenticated(redirect_false='taskapp-login')
@api_view(['GET'])
def show_grp_members(request, id):
    user = auth.get_user(request.session.get('user_email'))

    members_in_grp = models.GroupModel.objects.get(pk=id, groupowner=user)
    serialize = models.GroupModelSerializer(members_in_grp)

    return Response(serialize.data)


@auth.is_authenticated(redirect_false='taskapp-login')
@api_view(['POST'])
def add_members(request, id):
    user = auth.get_user(request.session.get('user_email'))
    data = json.loads(request.data)

    grp = models.GroupModel.objects.get(pk=id, groupowner=user)

    add_new_member = models.UserModel.objects.get(pk=data['email'])

    grp.groupusers.add(add_new_member)

    return Response({'response': 200})



