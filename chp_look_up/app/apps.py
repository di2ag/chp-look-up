from django.apps import AppConfig
from chp_data.chp_look_up.DataHandler import DataHandler
from django.core.management import call_command
from django.db import transaction
from tqdm import tqdm

class ChpLookUpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chp_look_up'
    label = 'chp_look_up'