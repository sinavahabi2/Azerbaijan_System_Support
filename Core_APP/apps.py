from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "Core_APP"
    verbose_name = "هسته اصلی سامانه"

    def ready(self):
        from . import signals