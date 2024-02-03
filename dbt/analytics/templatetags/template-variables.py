from django import template
import dbt.analytics
from dbt.analytics.views import PythonLogsDetailsView
register = template.Library()

@register.simple_tag
def get_nav_items():
    nav_items = {"General": [
                               ("Periodic Task","fa-solid fa-plus", "admin:index"),
                                  ("DBT Logs", "fa-solid fa-plus", "admin:index"),
                                     ("Python Logs", "fa-solid fa-plus", "admin:index"),
                                        ("SubProcess Logs", "fa-solid fa-plus", "admin:index"),
                                            ("Git Repos", "fa-solid fa-plus", "admin:index"),
                                               ("Profile Yamls", "fa-solid fa-plus", "admin:index"),
                                            ],
                 }

    return nav_items