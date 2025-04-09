from django.urls import path
from llmchatbot.views import *

app_name = "llmchatbot"

urlpatterns = [
    path('test/', test, name="test"),
    path('request_test/', request_test, name="request_test"),
    path('chat_with_openai/', chat_with_openai, name="chat_with_openai"),
]
