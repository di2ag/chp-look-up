from django.shortcuts import render

# Create your views here.
import logging
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import QueryIdentifier

class query(APIView):
    def post(self, request):
        query_processor = QueryIdentifier().getQueryProcessor(request=request)
        return query_processor.getResponse()
