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
            # POST 요청의 body에서 질문 데이터 추출
            data = json.loads(request.body)
            question = data.get('question', '')
            
            if not question:
                return JsonResponse({'error': '질문이 제공되지 않았습니다.'}, status=400)
            
            # OpenAI 클라이언트 생성
            client = OpenAI(api_key=settings.OPENAI_API)
            
            # OpenAI에 질문 전송
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            )
            
            # 응답에서 답변 추출
            answer = response.choices[0].message.content
            
            # JSON 형태로 응답 반환
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

            # 요청에서 JSON 데이터 파싱
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
            
            # API 응답에서 교정된 음식 이름 추출
            return JsonResponse(json.loads(response.choices[0].message.content))
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "올바르지 않은 JSON 형식입니다"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    # POST 요청이 아닌 경우
    return JsonResponse({"error": "POST 요청만 허용됩니다"}, status=405)