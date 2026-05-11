class AppRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "vulnerable":
            return "vulnerable_db"
        return "default"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, **hints):
        if app_label == "vulnerable":
            return db == "vulnerable_db"
        if app_label in ("auth", "contenttypes"):
            return True
        return db == "default"