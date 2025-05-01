from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

def db_test(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'request success! - chatbot'})
    else:
        return JsonResponse({'error': 'GET 요청만 허용됩니다.'}, status=405)