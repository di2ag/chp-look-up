from django.apps import AppConfig
from ChpData.chp_data.chp_look_up.DataHandler import DataHandler
from django.core.management import call_command
import inspect
class ChpLookUpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chp_look_up'

    def ready(self) -> None:
        for fn in inspect.getmembers(DataHandler, predicate=inspect.isfunction)
            print(fn)
        return super().ready()