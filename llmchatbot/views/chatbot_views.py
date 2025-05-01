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

from django.http import JsonResponse
from ..models import Food, Menu, FoodMenu, FeedBack

def db_test(request):
    latest_food = Food.objects.order_by('-id').first()
    latest_menu = Menu.objects.order_by('-id').first()
    latest_food_menu = FoodMenu.objects.order_by('-id').first()
    latest_feedback = FeedBack.objects.order_by('-id').first()

    response_data = {
        'latest_food': {
            'id': latest_food.id,
            'name': latest_food.name,
            'calorie': latest_food.calorie,
            'category': latest_food.category,
            'category_name': latest_food.get_category_display() if latest_food else None,
            'nutrition': latest_food.nutrition,
            'allergy': latest_food.allergy
        } if latest_food else None,
        
        'latest_menu': {
            'id': latest_menu.id,
            'date': latest_menu.date,
            'meal_type': latest_menu.meal_type,
            'meal_type_name': latest_menu.get_meal_type_display() if latest_menu else None,
            'evaluation': latest_menu.evaluation
        } if latest_menu else None,
        
        'latest_food_menu': {
            'id': latest_food_menu.id,
            'menu_id': latest_food_menu.menu_id,
            'food_id': latest_food_menu.food_id,
            'menu_info': str(latest_food_menu.menu) if latest_food_menu and latest_food_menu.menu else None,
            'food_info': str(latest_food_menu.food) if latest_food_menu and latest_food_menu.food else None
        } if latest_food_menu else None,
        
        'latest_feedback': {
            'id': latest_feedback.id,
            'food_menu_id': latest_feedback.food_menu_id,
            'score': latest_feedback.score,
            'evaluation': latest_feedback.evaluation,
            'created_at': latest_feedback.created_at,
            'food_menu_info': str(latest_feedback.food_menu) if latest_feedback and latest_feedback.food_menu else None
        } if latest_feedback else None
    }
    
    return JsonResponse(response_data)
