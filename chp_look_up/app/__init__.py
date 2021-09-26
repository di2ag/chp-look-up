from chp_look_up.trapi_interface import TrapiInterface
from chp_look_up.app.apps import *

def get_app_config():
    return ChpLookUpConfig

def get_trapi_interface(chp_look_up_config=None):
    if chp_look_up_config is None:
        chp_look_up_config = ChpLookUpConfig
    return TrapiInterface()

def get_curies():
    interface = get_trapi_interface()
    return interface.get_curies()

def get_meta_knowledge_graph():
    interface = get_trapi_interface()
    return {"foo":"goo"}
    #return interface.get_meta_knowledge_graph()
    
def get_response(consistent_queries):
    """ Should return app responses plus app_logs, status, and description information.
    """
    interface = get_trapi_interface()
    identified_queries = interface.identify_queries(consistent_queries)
    return {"foo":"goo"}