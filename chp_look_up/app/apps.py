from django.apps import AppConfig
from chp_data.chp_look_up.DataHandler import DataHandler
from django.core.management import call_command

class ChpLookUpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chp_look_up'
    label = 'chp_look_up'

    def ready(self) -> None:
        call_command("loaddata",DataHandler.getGeneToPathwayFixture())
        call_command("loaddate", DataHandler.getPathwayToGeneFixture())
        return super().ready()