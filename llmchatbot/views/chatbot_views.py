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
import requests
import traceback
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API)

# 스프링부트 URL 정보
# SPRINGBOOT_BASE_URL = "http://localhost:8080/api/team3/analytics/chatbot"
SPRINGBOOT_BASE_URL = "http://k8s-msaservices-7d023f0bb9-676035063.ap-northeast-2.elb.amazonaws.com/api/team3/analytics/chatbot"

class SimpleVectorDB:
    """
    간단한 메모리 기반 벡터 데이터베이스
    """
    def __init__(self):
        self.documents = []
        self.vectors = None
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), analyzer='char_wb')
    
    def add_documents(self, documents):
        """문서들을 벡터화하여 저장"""
        self.documents = documents
        self.vectors = self.vectorizer.fit_transform(documents)
    
    def search(self, query, top_k=10):
        """쿼리와 가장 유사한 문서들을 검색"""
        if not self.documents:
            return []
        
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.vectors)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                'document': self.documents[idx],
                'similarity': float(similarities[idx])
            })
        
        return results

food_vector_db = SimpleVectorDB()
feedback_vector_db = SimpleVectorDB()

def create_prompt_for_food_info(query, relevant_docs):
    """음식 정보 관련 프롬프트 생성"""
    context = "\n".join([doc['document'] for doc in relevant_docs])
    prompt = f"""당신은 학교 급식 정보를 제공하는 전문 어시스턴트입니다. 아래의 음식 정보를 바탕으로 사용자의 질문에 답변해주세요.

음식 정보:
{context}

사용자 질문: {query}

답변 시 다음 사항을 고려해주세요:
1. 구체적이고 정확한 정보를 제공하세요.
2. 영양소, 칼로리, 알러지 정보 등을 포함해서 답변하세요.
3. 친근하고 이해하기 쉬운 말로 답변하세요.
"""
    return prompt

def create_prompt_for_feedback_info(query, relevant_docs):
    """피드백 정보 관련 프롬프트 생성"""
    context = "\n".join([doc['document'] for doc in relevant_docs])
    prompt = f"""당신은 학교 급식 피드백 분석 전문가입니다. 아래의 피드백 정보를 바탕으로 사용자의 질문에 답변해주세요.

피드백 정보:
{context}

사용자 질문: {query}

답변 시 다음 사항을 고려해주세요:
1. 학생들의 평가 점수와 의견을 반영하여 답변하세요.
2. 어떤 음식이 인기가 있는지, 어떤 점이 좋거나 개선이 필요한지 분석해주세요.
3. 객관적이고 건설적인 의견을 제시하세요.
"""
    return prompt

def get_openai_response(prompt):
    """OpenAI API를 통해 응답 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for school lunch information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {str(e)}"

@csrf_exempt
@api_view(['POST'])
@swagger_auto_schema(
    operation_summary="basic chatbot request",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'category': openapi.Schema(type=openapi.TYPE_STRING, description="Category of the request (FOOD_INFO or FOOD_FEEDBACK_INFO)"),
            'question': openapi.Schema(type=openapi.TYPE_STRING, description="Question for the chatbot")
        },
        required=['category', 'question']
    )
)
def basic_chatbot_request(request):
    try:
        if not request.body:
            logger.error("빈 요청 본문이 수신되었습니다")
            return JsonResponse({"error": "빈 요청 본문"}, status=400)
        
        try:
            if hasattr(request, 'data'):
                data = request.data
            else:
                data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코드 오류: {str(e)}")
            return JsonResponse({"error": f"유효하지 않은 JSON 형식: {str(e)}"}, status=400)
        
        category = data.get('category')
        question = data.get('question')
        
        logger.info(f"카테고리: {category}, 질문: {question}")
        
        if not category or not question:
            return JsonResponse({"error": "Both category and question are required"}, status=400)
        
        if category == "FOOD_INFO":
            try:
                response = requests.get(f"{SPRINGBOOT_BASE_URL}/food-info")
                
                if response.status_code == 200:
                    food_data = response.json()

                    food_vector_db.add_documents(food_data)

                    relevant_docs = food_vector_db.search(question, top_k=10)

                    prompt = create_prompt_for_food_info(question, relevant_docs)
                    ai_response = get_openai_response(prompt)
                    
                    return JsonResponse({
                        "message": "성공했습니다",
                        "answer": ai_response,
                        "relevant_documents": relevant_docs[:5]
                    })
                else:
                    logger.error(f"Failed to retrieve food info: {response.status_code}")
                    return JsonResponse({"error": "Failed to retrieve food information"}, status=500)
            except requests.RequestException as e:
                logger.error(f"Request exception when fetching food info: {str(e)}")
                return JsonResponse({"error": f"Error connecting to Spring Boot: {str(e)}"}, status=500)
        
        elif category == "FOOD_FEEDBACK_INFO":
            try:
                response = requests.get(f"{SPRINGBOOT_BASE_URL}/feedback-info")
                
                if response.status_code == 200:
                    feedback_data = response.json()

                    feedback_vector_db.add_documents(feedback_data)

                    relevant_docs = feedback_vector_db.search(question, top_k=10)

                    prompt = create_prompt_for_feedback_info(question, relevant_docs)
                    ai_response = get_openai_response(prompt)
                    
                    return JsonResponse({
                        "message": "성공했습니다",
                        "answer": ai_response,
                        "relevant_documents": relevant_docs[:5]
                    })
                else:
                    logger.error(f"Failed to retrieve feedback info: {response.status_code}")
                    return JsonResponse({"error": "Failed to retrieve feedback information"}, status=500)
            except requests.RequestException as e:
                logger.error(f"Request exception when fetching feedback info: {str(e)}")
                return JsonResponse({"error": f"Error connecting to Spring Boot: {str(e)}"}, status=500)
        
        else:
            return JsonResponse({"error": "Invalid category. Must be FOOD_INFO or FOOD_FEEDBACK_INFO"}, status=400)
    
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)


def db_test(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'request success! - chatbot'})
    else:
        return JsonResponse({'error': 'GET 요청만 허용됩니다.'}, status=405)
    

### agent화
def determine_category(question):
    """OpenAI API를 통해 질문의 카테고리 결정"""
    try:
        prompt = f"""당신은 학교 급식 관련 질문을 분류하는 전문가입니다. 
사용자 질문을 분석하여 다음 두 가지 카테고리 중 하나를 선택해주세요:

1. FOOD_INFO: 음식 자체에 관한 영양소, 칼로리, 알러지 정보 등 음식 자체의 특성에 관한 질문
2. FOOD_FEEDBACK_INFO: 음식에 대한 학생들의 평가, 점수, 피드백 등 학생들의 반응에 관한 질문

사용자 질문: {question}

다음 JSON 형식으로만 응답해주세요:
{{
  "category": "선택한 카테고리(FOOD_INFO 또는 FOOD_FEEDBACK_INFO)",
  "reasoning": "왜 이 카테고리를 선택했는지에 대한 추론 과정"
}}

추론 과정은 단계별로 작성해주시고, 질문의 특징과 관련된 키워드를 분석하여 설명해주세요.
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorizes questions about school lunch."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        try:
            import re
            json_match = re.search(r'({[\s\S]*})', result)
            if json_match:
                result = json_match.group(0)
            
            category_data = json.loads(result)
            category = category_data.get("category")
            reasoning = category_data.get("reasoning")
            
            if reasoning:
                if isinstance(reasoning, list):
                    reasoning.append(f"CoT: 사용자 질문을 추론한 것 기반, [{category}] 카테고리로 설정하여 해당 백터db로 검색을 진행함.")
                else:
                    reasoning = f"{reasoning}\n\nCoT: 사용자 질문을 추론한 것 기반, [{category}] 카테고리로 설정하여 해당 백터db로 검색을 진행함."
            
            return category, reasoning
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse category JSON from OpenAI response: {result}")
            default_category = "FOOD_INFO"
            default_reasoning = f"Failed to parse category. Using default. Original response: {result}\n\n따라서, 사용자 질문을 추론하였을때 [{default_category}] 카테고리로 설정하여 해당 백터db로 검색을 진행합니다."
            return default_category, default_reasoning
        
    except Exception as e:
        logger.error(f"Error determining category: {str(e)}")
        default_category = "FOOD_INFO"
        default_reasoning = f"Error determining category: {str(e)}. Using default category.\n\n따라서, 사용자 질문을 추론하였을때 [{default_category}] 카테고리로 설정하여 해당 백터db로 검색을 진행합니다."
        return default_category, default_reasoning

@csrf_exempt
@api_view(['POST'])
@swagger_auto_schema(
    operation_summary="agent chatbot request without category",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'question': openapi.Schema(type=openapi.TYPE_STRING, description="Question for the chatbot")
        },
        required=['question']
    )
)
def agent_chatbot_request(request):
    try:
        if not request.body:
            logger.error("빈 요청 본문이 수신되었습니다")
            return JsonResponse({"error": "빈 요청 본문"}, status=400)
        
        try:
            if hasattr(request, 'data'):
                data = request.data
            else:
                data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코드 오류: {str(e)}")
            return JsonResponse({"error": f"유효하지 않은 JSON 형식: {str(e)}"}, status=400)
        
        question = data.get('question')
        
        logger.info(f"에이전트 챗봇 질문: {question}")
        
        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)
        
        # 카테고리 결정
        category, reasoning = determine_category(question)
        logger.info(f"결정된 카테고리: {category}, 추론: {reasoning}")
        
        if category == "FOOD_INFO":
            try:
                response = requests.get(f"{SPRINGBOOT_BASE_URL}/food-info")
                
                if response.status_code == 200:
                    food_data = response.json()

                    food_vector_db.add_documents(food_data)

                    relevant_docs = food_vector_db.search(question, top_k=10)

                    prompt = create_prompt_for_food_info(question, relevant_docs)
                    ai_response = get_openai_response(prompt)

                    if isinstance(reasoning, list):
                        reasoning = "\n".join(reasoning)
                    
                    return JsonResponse({
                        "message": "성공했습니다",
                        "answer": ai_response,
                        "relevant_documents": relevant_docs[:5],
                        "chainOfThought": reasoning
                    })
                else:
                    logger.error(f"Failed to retrieve food info: {response.status_code}")
                    return JsonResponse({"error": "Failed to retrieve food information"}, status=500)
            except requests.RequestException as e:
                logger.error(f"Request exception when fetching food info: {str(e)}")
                return JsonResponse({"error": f"Error connecting to Spring Boot: {str(e)}"}, status=500)
        
        elif category == "FOOD_FEEDBACK_INFO":
            try:
                response = requests.get(f"{SPRINGBOOT_BASE_URL}/feedback-info")
                
                if response.status_code == 200:
                    feedback_data = response.json()

                    feedback_vector_db.add_documents(feedback_data)

                    relevant_docs = feedback_vector_db.search(question, top_k=10)

                    prompt = create_prompt_for_feedback_info(question, relevant_docs)
                    ai_response = get_openai_response(prompt)

                    if isinstance(reasoning, list):
                        reasoning = "\n".join(reasoning)
                    
                    return JsonResponse({
                        "message": "성공했습니다",
                        "answer": ai_response,
                        "relevant_documents": relevant_docs[:5],
                        "chainOfThought": reasoning
                    })
                else:
                    logger.error(f"Failed to retrieve feedback info: {response.status_code}")
                    return JsonResponse({"error": "Failed to retrieve feedback information"}, status=500)
            except requests.RequestException as e:
                logger.error(f"Request exception when fetching feedback info: {str(e)}")
                return JsonResponse({"error": f"Error connecting to Spring Boot: {str(e)}"}, status=500)
        
        else:
            return JsonResponse({
                "error": "Invalid category determined", 
                "determined_category": category,
                "reasoning": reasoning
            }, status=400)
    
    except Exception as e:
        logger.error(f"Unhandled exception in agent chatbot: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({"error": f"Error processing request: {str(e)}"}, status=500)