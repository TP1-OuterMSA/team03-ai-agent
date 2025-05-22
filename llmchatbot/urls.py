from django.urls import path
from llmchatbot.views import *
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = "llmchatbot"

schema_view = get_schema_view(
    openapi.Info(
        title="Team3 - llm 및 rag기술을 활용한 ai 서비스 api",
        default_version='v1',
        description="llmchatbot",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    ### test api
    path('test/', test, name="test"),
    path('request_test/', request_test, name="request_test"),
    path('chat_with_openai/', chat_with_openai, name="chat_with_openai"),
    ### MS팀 ai 솔루션 api
    path('correct/', correct, name="correct"),
    path('categorization/', categorization, name="categorization"),
    path('detail_categorization/', detail_categorization, name="detail_categorization"),
    path('detail_food_analyze/', detail_food_analyze, name='detail_food_analyze'),
    ### ai 리포트
    path('create_report/', create_report, name='create_report'),
    ### ai 챗봇
    path('db_test/', db_test, name='db_test'),
    path('basic_chatbot_request/', basic_chatbot_request, name='basic_chatbot_request'),
    path('agent_chatbot_request/', agent_chatbot_request, name='agent_chatbot_request'),
    # Swagger URL
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]