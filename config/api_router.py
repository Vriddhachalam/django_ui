from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from dbt.analytics.views import (
    GitRepoAPIViewset,
    SSHKeyViewSets,
    InterValViewSet,
    AddPeriodicTask,
    PostYMALDetailsView,
    PythonLogsDetailsView,
    CrontabScheduleViewSet,
    DBTCurrentVersionView,
    RunDBTTask,
    RunPythonTask,
)
from django.urls import path
from django.conf.urls.static import static

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


app_name = "api"


router.register(r"git-repo", GitRepoAPIViewset, basename="git-repo")
router.register(r"git-ssh-key", SSHKeyViewSets, basename="ssh-key")
router.register(r"interval", InterValViewSet, basename="interval")
router.register(r"crontab", CrontabScheduleViewSet, basename="crontab")
router.register(r"periodic-task", AddPeriodicTask, basename="periodic-task")
router.register(r"profile_yaml", PostYMALDetailsView, basename="profile_yaml")
router.register(r"Python_logs", PythonLogsDetailsView, basename="Python_logs")

urlpatterns = [
    path(
        "dbt-current-version",
        DBTCurrentVersionView.as_view(),
        name="dbt-current-version",
    ),
    path("run-dbt-task", RunDBTTask.as_view(), name="run-dbt-task"),
    path("run-python-task", RunPythonTask.as_view(), name="run-python-task"),

    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += router.urls
