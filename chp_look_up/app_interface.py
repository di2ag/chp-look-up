from .trapi_interface import TrapiInterface
from .apps import *
from trapi_model.knowledge_graph import KnowledgeGraph
from trapi_model.meta_knowledge_graph import MetaKnowledgeGraph
from chp_utils.curie_database import CurieDatabase
from chp_utils.conflation import ConflationMap

def get_app_config(query):
    return ChpLookUpConfig

def get_trapi_interface(chp_look_up_config = get_app_config(None)):
    return TrapiInterface(trapi_version='1.2')

def get_meta_knowledge_graph() -> MetaKnowledgeGraph:
    interface = get_trapi_interface()
    return interface.get_meta_knowledge_graph()

def get_curies() -> CurieDatabase:
    interface = get_trapi_interface()
    return interface.get_curies()

def get_conflation_map() -> ConflationMap:
    interface = get_trapi_interface()
    return interface.get_conflation_map()
    
def get_response(consistent_queries) -> tuple:
    """ Should return app responses plus app_logs, status, and description information.
    """
    responses = []
    status:str = None
    description:str = None
    app_logs = []
    if not isinstance(consistent_queries, list):
        consistent_queries = [consistent_queries]

    for consistent_query in consistent_queries:
        interface = get_trapi_interface()
        identified_queries_tuple = interface.identify_queries(consistent_query)
        try:
            response = interface.query_database(identified_queries_tuple)
        except Exception as ex:
            response = consistent_query.get_copy()
        responses.append(response)
        app_logs.extend(interface.logger.to_dict())
    status = 'Success'

    return responses, app_logs, status, description
