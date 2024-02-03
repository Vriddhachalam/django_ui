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

from dbt.analytics import views
import dbt.analytics

admin.site.index_title = "Features area"

urlpatterns = [

    path("api/", include("config.api_router")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
     path("admin/", admin.site.urls,name="admin"),
     path('home', views.home, name = 'home'),
     path('python_logs_view', views.python_logs_view, name='FormView'),
     path('python_logs_form', views.python_logs_form, name='FormView'),
     path('dbt_logs_form', views.dbt_logs_form, name='FormView'),
     path('dbt_logs_view', views.dbt_logs_view, name='FormView'),
     path('dbt_jobs_view', views.dbt_jobs_view, name='FormView'),
    #  path('analytics', include('analytics.urls')),
     path('periodic_task_view', views.periodic_task_view, name='FormView'),
     path('periodic_task_form', views.periodic_task_form, name='FormView'),
     path('new_page', views.new_page_view, name='new_page'),
     path('reload_div', views.reload_div, name='reload_div'),
     path('profile_yaml_form', views.profile_yaml_form, name='profile_yaml_form'),
     path('profile_yaml_view', views.profile_yaml_view, name='profile_yaml_view'),
     path('periodic_task_add_form', views.periodic_task_add_form, name='FormView'),

     path('git_repo_form', views.git_repo_form, name='FormView'),
     path('git_repo_view', views.git_repo_view, name='FormView'),

    path("", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
