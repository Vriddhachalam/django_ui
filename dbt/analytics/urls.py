from django import urls
from django.contrib import admin
from django.urls.conf import include
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.generic import TemplateView
from django.views import defaults as default_views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from dbt.analytics import views


urlpatterns = [
    path('home', views.home, name = 'home'),
    path('python_logs_form', views.python_logs_form, name='FormView'),
    path('python_logs_view', views.python_logs_view, name='FormView'),
    path('periodic_task_form', views.periodic_task_form, name='FormView'),
    path('periodic_task_view', views.periodic_task_view, name='FormView'),
    path('periodic_task_add_form', views.periodic_task_add_form, name='FormView'),
    path('dbt_logs_form', views.dbt_logs_form, name='FormView'),
    path('dbt_logs_view', views.dbt_logs_view, name='FormView'),
    path('new_page', views.new_page_view, name='new_page'),
    path('reload_div', views.reload_div, name='reload_div'),
    path('profile_yaml_form', views.profile_yaml_form, name='profile_yaml_form'),
    path('profile_yaml_view', views.profile_yaml_view, name='profile_yaml_view'),
    path('git_repo_form', views.git_repo_form, name='FormView'),
    path('git_repo_view', views.git_repo_view, name='FormView'),

] 