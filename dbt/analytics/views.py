from django_celery_beat.models import IntervalSchedule, CrontabSchedule
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dbt.utils.common import load_dbt_current_version
from config.celery_app import python_runner_task,dbt_runner_task
from django.shortcuts import render
from django.template import context, loader
from django.http import HttpResponse, JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder

from django.db import connection

from dbt.analytics.models import (
    GitRepo,
    ProfileYAML,
    SSHKey,
    DBTLogs,
    DBTJobs,
    PythonLogs,
    PeriodicTask as PeriodicTaskModel,
)
from dbt.analytics.serializers import (
    GitRepoSerializer,
    IntervalScheduleSerializer,
    PeriodicTaskSerializer,
    ProfileYAMLSerializer,
    SSHKeySerializer,
    WritePeriodicTaskSerializer,
    CrontabScheduleSerializer,
    DBTCurrentVersionSerializer,
    PythonSerializer,
    RunTaskSerializer,
)

from dbt.analytics.forms import PythonLogsForm,PeriodicTaskForm,DbtLogsForm,ProfileYAMLForm, GitRepoForm

from django.shortcuts import render
from dbt.analytics.forms import PythonLogsForm


def python_logs_form(request):
      if request.method == 'POST':
        form = PythonLogsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Your review has been taken')

      else:
        form = PythonLogsForm()
        context = {
            'form':form
        }
      return render(request, "admin/analytics/python_logs_form.html", context)

def python_logs_view(request):
    # template= loader.get_template('admin/base.html')
    # change_list_template = 'admin/base_site.html'
    my_data = PythonLogs.objects.all() #for all the records 
    # one_data = PythonLogs.objects.get(pk=21) # 1 will return the first item change it depending on the data you want 
    context={

      'my_data':my_data,
    #   'one_data':one_data,

    } 

    return render(request, 'admin/analytics/python_logs_view.html',context)


    # item_list= PythonLogs.objects.all()
    # template= loader.get_template('admin/base.html')
    # change_list_template = 'admin/analytics/test.html'

    # context={
    #     'itemList': item_list,
    # }
    # return render(request, 'admin/analytics/test.html')



def periodic_task_form(request):
      if request.method == 'POST':
        form = PeriodicTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Your review has been taken')

      else:
        form = PeriodicTaskForm()
        context = {
            'form':form
        }
      return render(request, "admin/analytics/periodic_task_form.html", context)

def profile_yaml_form(request):
      if request.method == 'POST':
        form = ProfileYAMLForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Your review has been taken')

      else:
        form = ProfileYAMLForm()
        context = {
            'form':form
        }
      return render(request, "admin/analytics/profile_yaml_form.html", context)


def profile_yaml_view(request):

    with connection.cursor() as cursor:
        cursor.execute("SELECT key FROM authtoken_token LIMIT 1")  # Adjust the query as needed
        row = cursor.fetchone()
        if row:
            auth_token = row[0]

    return render(request, 'admin/analytics/profile_yaml_view.html',{'auth_token': auth_token})

def periodic_task_view(request):
    data = PeriodicTaskModel.objects.all().values()    

    with connection.cursor() as cursor:
        cursor.execute("SELECT key FROM authtoken_token LIMIT 1")  # Adjust the query as needed
        row = cursor.fetchone()
        if row:
            auth_token = row[0]

    next_id = DBTJobs.objects.last().job_id +1

    return render(request, 'admin/analytics/periodic_task_view.html', {'data': json.dumps( list(data) , cls=DjangoJSONEncoder),'auth_token': auth_token,'next_id': next_id})



def periodic_task_add_form(request):
    data = PeriodicTaskModel.objects.all().values()    

    with connection.cursor() as cursor:
        cursor.execute("SELECT key FROM authtoken_token LIMIT 1")  # Adjust the query as needed
        row = cursor.fetchone()
        if row:
            auth_token = row[0]

        cursor.execute("select id, clocked_time from django_celery_beat_clockedschedule order by id desc limit 1 ")
        # row = cursor.fetchone()
        # if row:
        #     new_clocked_value = row
        row = cursor.fetchone()
        if row:
            id, clocked_time = row
            new_clocked_value = json.dumps({'id': id, 'clocked_time': clocked_time}, cls=DjangoJSONEncoder)

                        
    

    next_id = DBTJobs.objects.last().job_id +1

    return render(request, 'admin/analytics/periodic_task_add_form.html', {'data': json.dumps( list(data) , cls=DjangoJSONEncoder),'auth_token': auth_token,'next_id': next_id, 'new_clocked_value':new_clocked_value})



def git_repo_form(request):
      if request.method == 'POST':
        form = GitRepoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Your review has been taken')

      else:
        form = GitRepoForm()
        context = {
            'form':form
        }
      return render(request, "admin/analytics/git_repo_form.html", context)

def git_repo_view(request):
    data = GitRepo.objects.all().values()    

    with connection.cursor() as cursor:
        cursor.execute("SELECT key FROM authtoken_token LIMIT 1")  # Adjust the query as needed
        row = cursor.fetchone()
        if row:
            auth_token = row[0]

    next_id = DBTJobs.objects.last().job_id +1

    return render(request, 'admin/analytics/git_repo_view.html', {'data': json.dumps( list(data) , cls=DjangoJSONEncoder),'auth_token': auth_token,'next_id': next_id})


def dbt_logs_form(request):
      if request.method == 'POST':
        form = DbtLogsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse('Your review has been taken')

      else:
        form = DbtLogsForm()
        context = {
            'form':form
        }
      return render(request, "admin/analytics/dbt_logs_form.html", context)

def dbt_logs_view(request):
    data = DBTLogs.objects.all().values()    
    return render(request, 'admin/analytics/dbt_logs_view.html', {'data': json.dumps( list(data) , cls=DjangoJSONEncoder)})

def dbt_jobs_view(request):
    jobs_data = DBTJobs.objects.all().values()  
    logs_data = DBTLogs.objects.all().values()  
    return render(request, 'admin/analytics/dbt_jobs_view.html', {'jobs_data': json.dumps( list(jobs_data) , cls=DjangoJSONEncoder), 'logs_data': json.dumps( list(logs_data) , cls=DjangoJSONEncoder)  })

def new_page_view(request):
    job_id_got = request.GET.get('job_id', None)

    if job_id_got:
        filtered_job_logs = DBTLogs.objects.filter(job_id=job_id_got).values()
        filtered_job = DBTJobs.objects.filter(job_id=job_id_got).values()
        next_id = DBTJobs.objects.last().job_id +1


    with connection.cursor() as cursor:
        cursor.execute("SELECT key FROM authtoken_token LIMIT 1")  # Adjust the query as needed
        row = cursor.fetchone()
        if row:
            auth_token = row[0]

    return render(request, 'admin/analytics/new_page.html', {'jobs_data': json.dumps( list(filtered_job) , cls=DjangoJSONEncoder), 'logs_data': json.dumps( list(filtered_job_logs) , cls=DjangoJSONEncoder), 'next_id':next_id ,'auth_token': auth_token })


def reload_div(request):
    # Logic to fetch updated content for the div
    dbt_stdout_values = list(DBTLogs.objects.all().values_list('dbt_stdout', flat=True))

    # Convert the values to HTML content
    updated_content = ""
    for stdout in dbt_stdout_values:
        updated_content += f"{stdout}"
    
    # updated_content = "<p>New content for the div</p>"

    return JsonResponse({'updated_content': updated_content})

def home(request):
  return render(request, "admin/analytics/home.html")

def logs_index(request):
    item_list= PythonLogs.objects.all()
    template= loader.get_template('admin/base.html')
    change_list_template = 'admin/change_list.html'

    context={
        'itemList': item_list,
    }
    return render(request, "admin/index.html")  

class GitRepoAPIViewset(ModelViewSet):
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]
    queryset = GitRepo.objects.all()
    serializer_class = GitRepoSerializer


class PostYMALDetailsView(ModelViewSet):
    serializer_class = ProfileYAMLSerializer
    queryset = ProfileYAML.objects.all()

class PythonLogsDetailsView(ModelViewSet):
    serializer_class = PythonSerializer
    queryset = PythonLogs.objects.all()


class SSHKeyViewSets(ModelViewSet):
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]
    queryset = SSHKey.objects.all()
    serializer_class = SSHKeySerializer


class InterValViewSet(ModelViewSet):
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer


class CrontabScheduleViewSet(ModelViewSet):
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSerializer


class AddPeriodicTask(ModelViewSet):
    queryset = PeriodicTaskModel.objects.all()
    serializer_class = WritePeriodicTaskSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return self.serializer_class
        else:
            return PeriodicTaskSerializer


class DBTCurrentVersionView(APIView):
    def get(self, request,):
        modules_version_data = load_dbt_current_version()
        serializer = DBTCurrentVersionSerializer(data=modules_version_data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class RunDBTTask(APIView):
    serializer_class = RunTaskSerializer

    def post(self, request, *args, **kwargs):
        serializer = RunTaskSerializer(data=request.data)
        if serializer.is_valid():
            task_id = serializer.validated_data["task_id"]
            task = PeriodicTaskModel.objects.get(id=task_id)
            args = eval(task.args) if task.args else []
            kwargs = eval(task.kwargs) if task.kwargs else {}
            dbt_runner_task.delay(*args, **kwargs)
            return Response(
                {"status": "Task has been initiated {} {}".format(args,kwargs)}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RunPythonTask(APIView):
    serializer_class = RunTaskSerializer

    def post(self, request, *args, **kwargs):
        serializer = RunTaskSerializer(data=request.data)
        if serializer.is_valid():
            task_id = serializer.validated_data["task_id"]
            task = PeriodicTaskModel.objects.get(id=task_id)
            args = eval(task.args) if task.args else []
            kwargs = eval(task.kwargs) if task.kwargs else {}
            python_runner_task.delay(*args, **kwargs)
            return Response(
                {"status": "Python Task has been initiated"}, status=status.HTTP_200_OK
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

