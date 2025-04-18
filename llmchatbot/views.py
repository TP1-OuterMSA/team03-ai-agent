from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def test(req):
    return render(req, 'llmchatbot/test.html')

def request_test(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'request success! cicd-test_end'})
    else:
        return JsonResponse({'error': 'GET 요청만 허용됩니다.'}, status=405)

@csrf_exempt
def chat_with_openai(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            
            if not question:
                return JsonResponse({'error': '질문이 제공되지 않았습니다.'}, status=400)
            
            client = OpenAI(api_key=settings.OPENAI_API)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            )
            
            answer = response.choices[0].message.content
            
            return JsonResponse({'answer': answer})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=405)
    
@csrf_exempt
def correct(request):
    if request.method == 'POST':
        try:
            client = OpenAI(api_key=settings.OPENAI_API)

            data = json.loads(request.body)
            food_name = data.get('food_name', '')
            
            if not food_name:
                return JsonResponse({"error": "food_name is required"}, status=400)

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 한국 음식 이름 맞춤법 검사 도우미입니다. 
                        주어진 한국 음식 이름에 오타가 있으면 올바른 철자로 수정하고, 
                        이미 올바른 경우에는 그대로 반환하세요.
                        음식 이름만 반환하고 다른 설명은 포함하지 마세요.
                        주의) 반환은 무조건 음식이름입니다. 요청값을 추론하여 무조건 음식이름만 반환하세요."""
                    },
                    {
                        "role": "user",
                        "content": food_name
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "food_correction",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "food_name": {"type": "string"}
                            },
                            "required": ["food_name"],
                            "additionalProperties": False
                        }
                    }
                },
                max_tokens=100
            )
            
            return JsonResponse(json.loads(response.choices[0].message.content))
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "올바르지 않은 JSON 형식입니다"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "POST 요청만 허용됩니다"}, status=405)

@csrf_exempt
def categorization(request):
    if request.method == 'POST':
        try:
            client = OpenAI(api_key=settings.OPENAI_API)
            data = json.loads(request.body)
            food_name = data.get('food_name', '')
            if not food_name:
                return JsonResponse({"error": "food_name is required"}, status=400)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """당신은 한국 음식을 분류하는 도우미입니다.
                        주어진 한국 음식 이름을 보고 다음 카테고리 중 하나로 분류하세요:
                        "RICE", "NOODLE", "SOUP", "SIDE", "MAIN", "DESSERT"
                        음식 이름에 가장 적합한 카테고리만 반환하고 다른 설명은 포함하지 마세요.
                        주의) 반환은 무조건 6개 카테고리 중 하나여야 합니다."""
                    },
                    {
                        "role": "user",
                        "content": food_name
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "food_category",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "enum": ["RICE", "NOODLE", "SOUP", "SIDE", "MAIN", "DESSERT"]
                                }
                            },
                            "required": ["category"],
                            "additionalProperties": False
                        }
                    }
                },
                max_tokens=100
            )
            
            return JsonResponse(json.loads(response.choices[0].message.content))
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "올바르지 않은 JSON 형식입니다"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "POST 요청만 허용됩니다"}, status=405)