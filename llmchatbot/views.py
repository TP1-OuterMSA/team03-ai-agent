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
        return JsonResponse({'message': 'request success! cicd-4'})
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