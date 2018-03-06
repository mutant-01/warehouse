from django.apps import AppConfig
from django.db.models.signals import post_delete, post_save


class DatastoreConfig(AppConfig):
    name = 'datastore'

    def ready(self):
        from datastore.signals import save_log, delete_log
        post_save.connect(
            save_log, sender='datastore.Data', dispatch_uid="save_log_handler"
        )
        post_delete.connect(
            delete_log, sender='datastore.Data', dispatch_uid="delete_log_handler"
        )
