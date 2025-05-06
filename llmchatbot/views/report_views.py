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
    

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['food_name'],
        properties={
            'food_name': openapi.Schema(type=openapi.TYPE_STRING, description='수정할 음식 이름')
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'food_name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    }
)
@api_view(['POST'])
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

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['food_name'],
        properties={
            'food_name': openapi.Schema(type=openapi.TYPE_STRING, description='음식 이름')
        }
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["RICE", "NOODLE", "SOUP", "SIDE", "MAIN", "DESSERT"]
                )
            }
        )
    }
)
@api_view(['POST'])
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

# @csrf_exempt
# def create_report(request):
#     """
#     Endpoint to receive school lunch report data from Spring Boot
#     """
#     if request.method == 'POST':
#         try:
#             request_body = request.body.decode('utf-8')
#             logger.info(f"Raw request body: {request_body}")
            
#             content_type = request.headers.get('Content-Type', '')
#             logger.info(f"Content-Type: {content_type}")
            
#             try:
#                 data = json.loads(request_body)
#             except json.JSONDecodeError as e:
#                 logger.error(f"JSON 파싱 오류: {str(e)}")
#                 return JsonResponse({'error': f'Invalid JSON data: {str(e)}'}, status=400)
            
#             logger.info("Received data from Spring Boot application:")
#             logger.info(f"Period Data: {data.get('period_data', '')}")
#             logger.info(f"Menu Evaluation Data: {data.get('menu_evaluation_data', '')}")
#             logger.info(f"Feedback Evaluation Data: {data.get('feed_back_evaluation_data', [])}")
#             logger.info(f"Average Calorie Data: {data.get('average_calorie_data', 0)}")
#             logger.info(f"Average Score Data: {data.get('average_score_data', 0)}")
#             logger.info(f"All Food Name Data: {data.get('all_food_name_data', '')}")
            
#             print("Received data from Spring Boot application:")
#             print(f"Period Data: {data.get('period_data', '')}")
#             print(f"Menu Evaluation Data: {data.get('menu_evaluation_data', '')}")
#             print(f"Feedback Evaluation Data: {data.get('feed_back_evaluation_data', [])}")
#             print(f"Average Calorie Data: {data.get('average_calorie_data', 0)}")
#             print(f"Average Score Data: {data.get('average_score_data', 0)}")
#             print(f"All Food Name Data: {data.get('all_food_name_data', '')}")
            
#             return JsonResponse({'message': '잘받았습니다'})
#         except Exception as e:
#             logger.error(f"오류 발생: {str(e)}")
#             return JsonResponse({'error': str(e)}, status=500)
    
#     return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


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
def create_report(request):
    if request.method == 'POST':
        try:
            request_body = request.body.decode('utf-8')
            logger.info(f"Raw request body: {request_body}")
            
            content_type = request.headers.get('Content-Type', '')
            logger.info(f"Content-Type: {content_type}")
            
            try:
                data = json.loads(request_body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON 파싱 오류: {str(e)}")
                return JsonResponse({'error': f'Invalid JSON data: {str(e)}'}, status=400)
            
            logger.info("Received data from Spring Boot application:")
            logger.info(f"Period Data: {data.get('period_data', '')}")
            logger.info(f"Menu Evaluation Data: {data.get('menu_evaluation_data', '')}")
            logger.info(f"Feedback Evaluation Data: {data.get('feed_back_evaluation_data', [])}")
            logger.info(f"Average Calorie Data: {data.get('average_calorie_data', 0)}")
            logger.info(f"Average Score Data: {data.get('average_score_data', 0)}")
            logger.info(f"All Food Name Data: {data.get('all_food_name_data', '')}")
            
            print("Received data from Spring Boot application:")
            print(f"Period Data: {data.get('period_data', '')}")
            print(f"Menu Evaluation Data: {data.get('menu_evaluation_data', '')}")
            print(f"Feedback Evaluation Data: {data.get('feed_back_evaluation_data', [])}")
            print(f"Average Calorie Data: {data.get('average_calorie_data', 0)}")
            print(f"Average Score Data: {data.get('average_score_data', 0)}")
            print(f"All Food Name Data: {data.get('all_food_name_data', '')}")
            
            report = generate_markdown_report(data)
            
            return JsonResponse({
                'message': '잘받았습니다', 
                'report': report
            })
        except Exception as e:
            logger.error(f"오류 발생: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

def generate_markdown_report(data):
    try:
        period_data = data.get('period_data', '기간 정보 없음')
        menu_evaluation_data = data.get('menu_evaluation_data', '')
        feed_back_evaluation_data = data.get('feed_back_evaluation_data', [])
        average_calorie_data = data.get('average_calorie_data', 0)
        average_score_data = data.get('average_score_data', 0)
        all_food_name_data = data.get('all_food_name_data', '')
        
        food_list = all_food_name_data.split(',') if all_food_name_data else []
        
        system_prompt = """
당신은 학교 급식 분석 전문가이며, 고품질의 마크다운 보고서를 작성해야 합니다. 
다음 지침을 철저히 따라 급식 데이터를 분석하고 구조화된 보고서를 생성하세요:

1. 마크다운 문법을 활용하여 시각적으로 아름답고 구조화된 보고서를 작성하세요.
2. 적절한 이모지를 사용하여 보고서를 생동감 있게 만드세요.
3. 전문적이고 통찰력 있는 분석을 제공하세요.
4. 보고서는 5개 섹션으로 구성하며, 각 섹션은 헤딩과 구분선으로 명확히 분리하세요.
5. 모든 분석은 데이터에 기반하여 작성하되, 필요한 경우 영양학적 지식을 활용하여 보완하세요.
6. 보고서는 상세하고 정성껏 작성하며, 최소 1000단어 이상이 되도록 충실하게 분석하세요.
7. 각 섹션마다 요약 및 권장사항을 포함하여 실질적인 개선점을 제시하세요.
8. 직접 음식의 평점을 더하거나 평균을 내거나 하는, 실수를 할 수 있는 숫자계산 작업은 하지마세요. 주어진 데이터만을 기반해서 작성해주세요.

보고서 작성 시 각 섹션을 빠짐없이 포함하고, 데이터에 기반한 깊이 있는 분석을 제공하세요.
(중요!) 절대로 지어내서는 안되며 거짓정보를 작성하면 안됩니다. 꼭 주어진 데이터를 기반으로 해서만 보고서를 작성하세요!
"""

        user_prompt = f"""
주어진 학교 급식 데이터를 바탕으로 마크다운 형식의 상세 보고서를 작성해주세요. 보고서에는 다음 섹션이 포함되어야 합니다:

## 데이터 정보
- 분석 기간: {period_data}
- 메뉴 평가 데이터: "{menu_evaluation_data}"
- 개별 음식 피드백: {json.dumps(feed_back_evaluation_data, ensure_ascii=False)}
- 평균 칼로리: {average_calorie_data}
- 평균 평점: {average_score_data}
- 제공된 음식 목록: {json.dumps(food_list, ensure_ascii=False)}

## 보고서 구성 요구사항
1. **제목**: "# AI분석 보고서 - {period_data} 분석 일지"로 시작하세요.

2. **메뉴 종합 평가**:
   - 메뉴 평가 데이터를 바탕으로 학생들의 전반적인 평가를 요약하세요.
   - 전문가 관점에서 개선점과 좋은 점을 분석하세요.
   - 다양한 마크다운 요소(인용문, 강조 등)를 활용하여 시각적으로 구조화하세요.

3. **개별 음식 피드백 분석**:
   - 각 음식별로 평가를 요약하고, 적절한 이모지를 사용하세요.
   - 음식별 강점과 개선점을 분석하세요.
   - 특히 주목할 만한 음식(매우 좋거나 나쁜 평가)을 강조하세요.
   - 전체 음식에 대한 종합적인 전문가 피드백을 제공하세요.
   - (중요) 전반적으로 불만이 있는 피드백을 위주로 완벽 분석하세요.

4. **제공된 음식 목록**:
   - 제공된 모든 음식 데이터를 마크다운 표 형식으로 정리하세요.
   - 가능하면 음식을 카테고리별로 분류하여 표시하세요.
   - 표는 시각적으로 깔끔하게 정렬하세요.
   - (중요) 지어내지말고 첨부되어 들어온 제공된 음식 목록 데이터만을 그냥 다 출력하면 됩니다.

5. **종합 분석 및 결론**:
   - 평균 칼로리({average_calorie_data})와 평균 평점({average_score_data})을 분석하세요.
   - 영양학적 관점에서 급식의 품질을 평가하세요.
   - 학생 만족도와 영양 균형에 대한 종합적인 결론을 제시하세요.
   - 향후 개선을 위한 구체적인 권장사항을 제안하세요.
   - (중요) 불만적인 피드백을 기반 어떻게 개선하면 좋을지도 작성하세요.

보고서는 마크다운 형식으로 작성하되, 다음 요소를 반드시 포함하세요:
- 섹션별 헤딩(#, ##, ### 등)
- 목록(순서 있는 목록과 순서 없는 목록)
- 강조(볼드, 이탤릭)
- 인용문
- 표
- 수평선
- 다양한 이모지

매우 상세하고 정성스럽게 작성하여, 실질적인 가치가 있는 보고서를 만들어주세요. 각 섹션이 충분히 길고 분석이 깊이 있게 이루어지도록 작성해주세요.

(중요!) 직접 피드백 데이터의 평점 데이터를 더하거나 평균을 내거나 하지마세요, 실수를 할 수 있는 숫자계산 작업은 하지마세요. 주어진 데이터만을 기반해서 작성해주세요. 이미 계산되어 주어진 평점데이터가 있으니 그것을 활용하면 됩니다. 피드백에 대한 개별 음식에 대한 스코어를 평균을 내거나 하지마세요. 계산 실수가 들어갈 수 있습니다.
(중요!) 절대로 지어내서는 안되며 거짓정보를 작성하면 안됩니다. 꼭 주어진 데이터를 기반으로 해서만 보고서를 작성하세요!
"""


        client = OpenAI(api_key=settings.OPENAI_API)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )

        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"보고서 생성 중 오류 발생: {str(e)}")
        return f"보고서 생성 중 오류가 발생했습니다: {str(e)}"