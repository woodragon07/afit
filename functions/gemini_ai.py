# functions/gemini_ai.py - Gemini AI 관련 함수
import re
import os
import json
import google.generativeai as genai
from functions.common_logger import get_logger
from functions.price_analyzer import is_lowest_price_request

# 모듈 로거 가져오기
logger = get_logger(__name__)

# Gemini API 키 설정 함수
def initialize_gemini():
    """Gemini API 초기화 함수"""
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.warning("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
            return False
        genai.configure(api_key=gemini_api_key)
        return True
    except Exception as e:
        logger.error(f"Gemini API 키 설정 오류: {e}")
        return False

# 초기화 실행
initialize_gemini()

def get_best_gemini_model():
    """사용 가능한 최적의 Gemini 모델을 가져오는 함수"""
    try:
        # 우선순위에 따라 모델 시도
        models_to_try = [
            "gemini-1.5-pro",
            "gemini-pro",
            "gemini-1.5-flash"
        ]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                logger.info(f"Gemini 모델 '{model_name}' 사용")
                return model
            except Exception as e:
                logger.warning(f"Gemini 모델 '{model_name}' 로드 실패: {e}")
                continue
                
        # 실패 시 기본 모델 사용
        logger.warning("기본 Gemini 모델로 폴백")
        return genai.GenerativeModel("gemini-flash")
    except Exception as e:
        logger.error(f"Gemini 모델 로드 오류: {e}")
        raise

def clean_gemini_response(raw):
    """Gemini 응답에서 코드 블록과 불필요한 부분을 제거하는 함수"""
    try:
        if not raw:
            return ""
            
        # 코드 블록 제거
        if "```" in raw:
            # 코드 블록 시작과 끝 사이의 내용 추출
            pattern = r"```(?:json)?(.*?)```"
            matches = re.findall(pattern, raw, re.DOTALL)
            if matches:
                return matches[0].strip()
        
        # JSON 형식 추출 시도
        json_pattern = r"\{.*\}"
        json_match = re.search(json_pattern, raw, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()
            
        return raw.strip()
    except Exception as e:
        logger.error(f"응답 정제 오류: {e}")
        return raw

def analyze_user_intent_with_gemini(user_message):
    """Gemini AI를 사용하여 사용자 메시지 의도와 필요 정보 추출"""
    try:
        # 최저가 요청인지 미리 확인 (백업)
        is_lowest_price = is_lowest_price_request(user_message)
        logger.debug(f"최저가 요청 여부: {is_lowest_price}")
        
        # 최적 모델 가져오기
        model = get_best_gemini_model()
        
        prompt = f"""
        당신은 쇼핑 검색 전문가이자 자연어 처리 분석가로서, 사용자의 메시지를 분석하여 쇼핑 관련 요청을 정확하게 분류하고 필요한 정보를 추출해야 합니다.

        사용자의 메시지: "{user_message}"

        다음 JSON 형식에 맞게, 오직 JSON 객체만을 반환하세요. 결과에 어떠한 부가 설명, 주석, 또는 추가 텍스트를 포함하지 말고, 반드시 아래 JSON 스키마를 준수하세요. 모든 숫자 값은 숫자형으로, 사용하지 않는 값은 null, 요청이 아닌 배열은 빈 배열([])로 표시하세요.

        JSON 객체의 필드는 다음과 같습니다:
        {{
        "is_shopping_request": true/false,  // 사용자의 메시지가 상품 검색 또는 쇼핑 관련 요청인지 여부. 요청이 아니면 false.
        "request_type": "product_search" 또는 "lowest_price" 또는 "general_question",  // 요청 유형:
            // - "product_search": 일반적인 상품 검색,
            // - "lowest_price": 최저가 검색,
            // - "general_question": 쇼핑 외 일반 질문.
        "product_keywords": ["검색 키워드1", "검색 키워드2", ...],  // 효과적인 상품 검색을 위한 핵심 키워드를 최대 10개까지 배열로 반환. 요청이 아니면 빈 배열.
        "attributes": ["특성1", "특성2", ...],  // 사용자가 언급한 상품의 특성 (예: 방수, 경량, 저소음 등).
        "price_min": 최소가격,  // 사용자가 언급한 최소 가격(숫자만). 언급하지 않았다면 null.
        "price_max": 최대가격,  // 사용자가 언급한 최대 가격(숫자만). 언급하지 않았다면 null.
        "specific_product": "정확한 제품명",  // 사용자가 특정 제품명을 언급한 경우 해당 이름을 반환, 그렇지 않으면 null.
        "brand_preference": "선호 브랜드명"  // 사용자가 선호하는 브랜드를 언급한 경우 해당 브랜드명을 반환, 그렇지 않으면 null.
        }}

        추가 지침:
        1. 메시지가 복잡하거나 애매한 경우에도, 가능한 한 구체적으로 정보를 추출하세요.
        2. 사용자의 메시지가 쇼핑 요청이 아닐 경우, "is_shopping_request"는 false로 설정하고, 나머지 필드는 null 또는 빈 배열로 반환하세요.
        3. 반드시 결과는 오직 JSON 객체만 출력해야 하며, 어떠한 설명, 주석, 추가 텍스트도 포함하지 말 것.
        4. 반환하는 JSON 객체는 모든 필드를 반드시 포함하며, 데이터 타입(숫자, 불리언, 문자열, 배열, null)을 정확히 준수할 것.

        예시 1: 사용자 메시지: "삼성 갤럭시 S23 울트라 최저가 알려줘"
        출력 예시:
        {{
        "is_shopping_request": true,
        "request_type": "lowest_price",
        "product_keywords": ["삼성 갤럭시 S23 울트라"],
        "attributes": [],
        "price_min": null,
        "price_max": null,
        "specific_product": "갤럭시 S23 울트라",
        "brand_preference": "삼성"
        }}

        예시 2: 사용자 메시지: "방수가 되는 20만원 이하 블루투스 스피커 추천해줘"
        출력 예시:
        {{
        "is_shopping_request": true,
        "request_type": "product_search",
        "product_keywords": ["블루투스 스피커"],
        "attributes": ["방수"],
        "price_min": null,
        "price_max": 200000,
        "specific_product": null,
        "brand_preference": null
        }}

        추가 지침:
        5. 이 메시지는 대화의 일부입니다. 만약 이전 대화 내용(예: "00에 필요한 게 뭐가 있을까?")이 있다면, 그 맥락을 고려하여 후속 질문을 포함한 더욱 구체적이고 자연스러운 응답을 생성하세요. 예를 들어, "간편식 추천해줘"에 대해서는 "여기 A, B, C 등의 제품이 있습니다. 어떤 종류를 찾으시나요?"와 같이 답변할 수 있습니다.
        6. 추가 지침에 "만약 검색 결과가 여러 범주로 나뉜다면, 사용자에게 '어떤 종류의 [검색 키워드]를 찾으시나요?'와 같은 후속 질문을 포함하여 응답하세요."
"""
        
        # API 호출
        response = model.generate_content(prompt)
        raw_text = response.text
        cleaned_text = clean_gemini_response(raw_text)
        
        # JSON 파싱 시도
        try:
            result = json.loads(cleaned_text)
            
            # 최저가 요청인데 Gemini가 감지 못했을 경우 보완
            if is_lowest_price and result.get("request_type") != "lowest_price":
                result["request_type"] = "lowest_price"
                logger.info("최저가 요청 감지로 request_type 수정됨")
                
            # 키워드가 너무 많으면 중요한 것만 유지
            if len(result.get("product_keywords", [])) > 3:
                result["product_keywords"] = result["product_keywords"][:3]
            
            # attributes가 없으면 빈 배열 추가
            if "attributes" not in result:
                result["attributes"] = []
                
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e} - 원본: {cleaned_text}")
            # 기본값 반환
            return {
                "is_shopping_request": True,
                "request_type": "product_search" if not is_lowest_price else "lowest_price",
                "product_keywords": [user_message],
                "attributes": [],
                "price_min": None,
                "price_max": None,
                "specific_product": None,
                "brand_preference": None
            }
        
    except Exception as e:
        logger.error(f"Gemini 분석 오류: {e}")
        # 오류 발생 시 기본값 반환
        return {
            "is_shopping_request": True,
            "request_type": "product_search",
            "product_keywords": [user_message],
            "attributes": [],
            "price_min": None,
            "price_max": None,
            "specific_product": None,
            "brand_preference": None
        }

def get_non_shopping_response(user_message):
    """쇼핑 의도가 없는 메시지에 대한 응답"""
    try:
        # 안정적인 모델 선택
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        당신은 친절한 쇼핑 도우미입니다. 사용자가 쇼핑과 관련 없는 질문을 했습니다.
        짧고 친절하게 응답하고, 쇼핑 관련 질문을 유도해보세요.
        응답은 2-3문장 이내로 간결하게 작성하세요.
        
        사용자 메시지: "{user_message}"
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"일반 응답 생성 오류: {e}")
        return "안녕하세요! 저는 쇼핑 도우미입니다. 어떤 상품을 찾으시나요?"