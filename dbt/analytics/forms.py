
# import form class from django
from django import forms

# import GeeksModel from models.py
from dbt.analytics.models import (
    GitRepo,
    ProfileYAML,
    SSHKey,
    PythonLogs,
    DBTLogs,
    PeriodicTask as PeriodicTaskModel,
)

# create a ModelForm
class PythonLogsForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = PythonLogs
        fields = "__all__"

class ProfileYAMLForm(forms.ModelForm):
    # specify the name of model to use
    # profile_yml = forms.CharField(widget=forms.Textarea(attrs={'cols': 40, 'rows': 10, 'maxlength': 4000}))
    class Meta:
        model = ProfileYAML
        fields = "__all__"        

class PeriodicTaskForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = PeriodicTaskModel
        exclude=['expires','expire_seconds','queue','exchange','routing_key','priority','headers']
        fields = "__all__"

class DbtLogsForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = DBTLogs
        fields = "__all__"

class GitRepoForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = GitRepo
        fields = "__all__"