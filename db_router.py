from django.conf import settings
from django.apps import apps

internal_apps = set(settings.INTERNAL_APPS)
internal_app_labels = set()
for app_config in apps.get_app_configs():
    if app_config.name in internal_apps:
        internal_app_labels.add(app_config.label)


class AppRouter:
    DJANGO_INTERNAL_APPS = internal_app_labels

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "secure":
            return "secure_db"
        if model._meta.app_label == "vulnerable":
            return "vulnerable_db"
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, **hints):
        if app_label == "secure":
            return db == "secure_db"
        if app_label == "vulnerable":
            return db == "vulnerable_db"
        if app_label in self.DJANGO_INTERNAL_APPS:
            return db in ("secure_db", "vulnerable_db")
        return False