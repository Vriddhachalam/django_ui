from django import forms
from django.contrib import admin, messages
from django.forms import ModelForm, PasswordInput
from celery import current_app
from django.contrib.auth.models import Group


from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponse

from django.contrib.sites.models import Site
from django.forms.widgets import Select
from celery.utils import cached_property
from django_celery_beat.admin import (
    PeriodicTaskAdmin as BasePeriodicTaskAdmin,
    PeriodicTaskForm as BasePeriodicTaskForm,
)
from dbt.users.models import User

from dbt.analytics.models import (
    DBTLogs,
    DBTJobs,
    PythonLogs,
    GitRepo,
    ProfileYAML,
    SubProcessLog,
    PeriodicTask,
)
from dbt.utils.common import clone_git_repo


class GitRepoForm(ModelForm):
    url = forms.CharField(widget=PasswordInput())

    class Meta:
        model = GitRepo
        fields = "__all__"

class DbtLogForm(ModelForm):

    class Meta:
        model = DBTLogs
        fields = "__all__"

@admin.register(DBTJobs)
class DBTJobsLAdmin(admin.ModelAdmin):
    list_display = [
        "job_id_link",
        "commands",        
        # "job_id",
        "success",
        "created_at",
        "completed_at",
        "repository",
        "profile_yml",
        "periodic_task",
        "status",
        ]

    def job_id_link(self, obj):
        return format_html('<a href="/analytics/dbtlogs/?job_id={}">{}</a>', obj.job_id, obj.job_id)

    job_id_link.allow_tags=True

@admin.register(DBTLogs)
class DBTLogsLAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "job_id",
        "completed_at",
        "success",
        "repository_used_name",
        "command",
        # "previous_command",
        "periodic_task_name",
        "status",
        "profile_yml_used_name",
    ]
    readonly_fields = [
        "repository_used_name",
        "periodic_task_name",
        "profile_yml_used_name",
    ]
    search_fields = ("job_id", "command")
    list_filter = ("job_id", "command")

@admin.register(PythonLogs)
class PythonLogsLAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "completed_at",
        "success",
        "repository_used_name",
        "command",
        "previous_command",
        "periodic_task_name",
        "profile_yml_used_name",
    ]
    readonly_fields = [
        "repository_used_name",
        "periodic_task_name",
        "profile_yml_used_name",
    ]

    search_fields = ("periodic_task_name", "created_at")
    list_filter = ("periodic_task_name", "created_at")

    # # change_form_template = 'admin/analytics/change_form.html'
    # # change_list_template = 'admin/analytics/change_list.html'

    # # def change_view(self, request, object_id, form_url="", extra_context=None):
    # #     extra_context = extra_context or {}
    # #     post = PythonLogs.objects.get(id=object_id)
    # #     extra_context["form"] = self.get_form(instance=post, request=request)
    # #     return super(PythonLogsLAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        change_form_template = 'admin/change_form.html'
        extra_context = extra_context or {}
        # extra_context['form'] = self.get_form(request)
        return super(PythonLogsLAdmin, self).add_view(request, extra_context=extra_context)


    def changelist_view(self, request, extra_context=None):
        change_list_template = 'admin/change_list.html'
        extra_context = {'title': 'Select Python logs to Change'}
        extra_context = extra_context or {}
        created_at = PythonLogs.objects.all().values_list('created_at', flat=True).distinct()
        completed_at = PythonLogs.objects.all().values_list('completed_at', flat=True).distinct()
        success = PythonLogs.objects.all().values_list('success', flat=True).distinct()
        repository_used_name  = PythonLogs.objects.all().values_list('repository_used_name', flat=True).distinct()
        command  = PythonLogs.objects.all().values_list('command', flat=True).distinct()
        # previous_command  = PythonLogs.objects.all().values_list('previous_command', flat=True).distinct()
        periodic_task_name = PythonLogs.objects.all().values_list('periodic_task_name', flat=True).distinct()
        profile_yml_used_name  = PythonLogs.objects.all().values_list('profile_yml_used_name', flat=True).distinct()
        extra_context.update({
            "created_at": created_at,
            "completed_at": completed_at,
            "success": success,
            "repository_used_name": repository_used_name,
            "command": command,
            # "previous_command":previous_command,
            "periodic_task_name":periodic_task_name,
            "profile_yml_used_name":profile_yml_used_name

        })
        return super().changelist_view(request, extra_context=extra_context)


    def python_logs_index(request):
      item_list= PythonLogs.objects.all()
      template= loader.get_template('admin/base.html')

      context={
        'itemList': item_list,
      }
      return HttpResponse(template.render(context, request))


@admin.register(ProfileYAML)
class ProfileYAMLAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "profile_yml",
    ]

    def has_add_permission(self, request):
        count = ProfileYAML.objects.all().count()
        if count < 2:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GitRepo)
class GitRepoAdmin(admin.ModelAdmin):
    # form = GitRepoForm
    list_display = [
        "id",
        "name",
        "public_key",
    ]

    def save_model(self, request, obj, form, change):
        obj.save()
        result, msg = clone_git_repo(obj)
        if result:
            ...
        else:
            obj.delete()
            messages.error(request, f"Something is wrong while git cloning {msg}")


@admin.register(SubProcessLog)
class SubprocessAdmin(admin.ModelAdmin):
    list_display = [
        "created_at",
        "details",
    ]


class ProfileSelectWidget(Select):
    """Widget that lets you choose between task names."""

    celery_app = current_app
    _choices = None

    def profiles_as_choices(self):
        _ = self._modules  # noqa
        tasks = list(
            sorted(
                name for name in self.celery_app.tasks if not name.startswith("celery.")
            )
        )
        return (("", ""),) + tuple(zip(tasks, tasks))

    @property
    def choices(self):
        if self._choices is None:
            self._choices = self.profiles_as_choices()
        return self._choices

    @choices.setter
    def choices(self, _):
        pass

    @cached_property
    def _modules(self):
        self.celery_app.loader.import_default_modules()


class ProfileChoiceField(forms.ChoiceField):
    widget = ProfileSelectWidget

    def valid_value(self, value):
        return True


class PeriodicTaskForm(BasePeriodicTaskForm):
    profile_yml = ProfileChoiceField(
        label="Profile YAML",
        required=False,
    )

    class Meta:
        model = PeriodicTask
        exclude = ()


class PeriodicTaskAdmin(BasePeriodicTaskAdmin):
    # form = PeriodicTaskForm
    model = PeriodicTask
    list_display = ('__str__', 'id' , 'enabled', 'interval', 'start_time',
                    'last_run_at', 'one_off')
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "git_repo",
                    "profile_yml",
                    "regtask",
                    "task",
                    "enabled",
                    "description",
                ),
                "classes": ("extrapretty", "wide"),
            },
        ),
        (
            "Schedule",
            {
                "fields": (
                    "interval",
                    "crontab",
                    "solar",
                    "clocked",
                    "start_time",
                    "last_run_at",
                    "one_off",
                ),
                "classes": ("extrapretty", "wide"),
            },
        ),
        (
            "Arguments",
            {
                "fields": ("args",),
                "classes": ("extrapretty", "wide", "collapse", "in"),
            },
        ),
        # (
        #     "Execution Options",
        #     {
        #         "fields": (
        #             "expires",
        #             "expire_seconds",
        #             "queue",
        #             "exchange",
        #             "routing_key",
        #             "priority",
        #             "headers",
        #         ),
        #         "classes": ("extrapretty", "wide", "collapse", "in"),
        #     },
        # ),
    )


#

if PeriodicTask in admin.site._registry:
    admin.site.unregister(PeriodicTask)
admin.site.register(PeriodicTask, PeriodicTaskAdmin)

# admin.site.unregister(Group)
# admin.site.unregister(Site)

admin.site.register(User)