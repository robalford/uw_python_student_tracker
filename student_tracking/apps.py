from importlib import import_module

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):

    name = "student_tracking"

    def ready(self):
        import_module("student_tracking.receivers")
