# functions/price_analyzer.py - 가격 분석 관련 함수
import re
from functions.common_logger import get_logger

# 모듈 로거 가져오기
logger = get_logger(__name__)

def extract_price_range(text):
    """텍스트에서 다양한 형식의 가격 범위를 추출하는 함수"""
    try:
        if not text:
            return None
            
        # '만원대' 패턴 (예: 10만원대)
        match = re.search(r'(\d+)만원대', text)
        if match:
            base = int(match.group(1))
            return {"min": base * 10000, "max": (base + 10) * 10000 - 1, "display": f"{base}만원대"}
        
        # '만원 이하/미만' 패턴
        match = re.search(r'(\d+)만원\s*(이하|미만)', text)
        if match:
            limit = int(match.group(1)) * 10000
            if match.group(2) == '미만':
                limit -= 1
            return {"max": limit, "display": f"{match.group(1)}만원 {match.group(2)}"}
        
        # '만원 이상/초과' 패턴
        match = re.search(r'(\d+)만원\s*(이상|초과)', text)
        if match:
            limit = int(match.group(1)) * 10000
            if match.group(2) == '초과':
                limit += 1
            return {"min": limit, "display": f"{match.group(1)}만원 {match.group(2)}"}
        
        # '~만원' 패턴 (예: 5~10만원)
        match = re.search(r'(\d+)~(\d+)만원', text)
        if match:
            min_price = int(match.group(1)) * 10000
            max_price = int(match.group(2)) * 10000
            return {"min": min_price, "max": max_price, "display": f"{match.group(1)}~{match.group(2)}만원"}
        
        # '원 이하/미만' 패턴
        match = re.search(r'(\d+(?:,\d+)*)원\s*(이하|미만)', text)
        if match:
            price_str = match.group(1).replace(',', '')
            limit = int(price_str)
            if match.group(2) == '미만':
                limit -= 1
            return {"max": limit, "display": f"{match.group(1)}원 {match.group(2)}"}
        
        # '원 이상/초과' 패턴
        match = re.search(r'(\d+(?:,\d+)*)원\s*(이상|초과)', text)
        if match:
            price_str = match.group(1).replace(',', '')
            limit = int(price_str)
            if match.group(2) == '초과':
                limit += 1
            return {"min": limit, "display": f"{match.group(1)}원 {match.group(2)}"}
            
        return None
    except Exception as e:
        logger.error(f"가격 범위 추출 오류: {e}")
        return None

def is_lowest_price_request(message):
    """메시지가 최저가 요청인지 확인하는 함수"""
    if not message:
        return False
        
    try:
        lowest_price_patterns = [
        r'최저가',
        r'최저\s*가격',
        r'최소가',
        r'최소\s*가격',
        r'최소금액',
        r'가장\s*싼',
        r'제일\s*싼',
        r'가장\s*저렴한',
        r'제일\s*저렴한',
        r'가격이\s*제일\s*낮은',
        r'가장\s*낮은\s*가격',
        r'싸게\s*파는',
        r'싸게\s*살\s*수',
        r'세일\s*하는',
        r'특가',
        r'특가\s*판매',
        r'할인\s*행사',
        r'할인\s*중',
        r'할인\s*많이',
        r'좋은\s*가격',
        r'가성비',
        r'최고의\s*가성비'
    ]
        # 최저가 관련 패턴이 있는지 확인
        for pattern in lowest_price_patterns:
            if re.search(pattern, message, re.IGNORECASE):  # 대소문자 무시
                return True
        
        return False
    except Exception as e:
        logger.error(f"최저가 요청 체크 오류: {e}")
        return False