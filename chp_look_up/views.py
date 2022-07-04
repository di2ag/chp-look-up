from textwrap import indent
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from chp_look_up.app_interface import get_response, get_meta_knowledge_graph, get_curies
import logging
import json
from trapi_model.query import Query
from sys import maxsize
# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function


def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)


logging.Logger.note = note  # type: ignore
logger = logging.getLogger(__name__)


def process_request(request, trapi_version):
    """ Helper function that extracts the query from the message."""

    logger.info('Starting query.')
    query = Query.load(
        trapi_version,
        biolink_version=None,
        query=request.data
    )

    logger.info('Query loaded')

    return query

class query(APIView):

    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(query, self).__init__(**kwargs)

    def post(self, request):
        query = process_request(request, trapi_version=self.trapi_version)
        response = get_response(query)
        response = response[0][0]
        response = response.to_dict()
        return JsonResponse(response)  # type:ignore

class meta_knowledge_graph(APIView):

    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(meta_knowledge_graph, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            # Get merged meta KG
            meta_knowledge_graph = get_meta_knowledge_graph()
            return JsonResponse(meta_knowledge_graph.to_dict())


class curies(APIView):

    def __init__(self, trapi_version='1.2', **kwargs):
        self.trapi_version = trapi_version
        super(curies, self).__init__(**kwargs)

    def get(self, request):
        if request.method == 'GET':
            # Get all chp app curies
            curies_db = get_curies()
            return JsonResponse(curies_db.to_dict())
