# functions/utils.py (공통 함수 파일)
import re
import urllib.parse
import requests
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from functions.common_logger import get_logger

# 모듈 로거 생성
logger = get_logger(__name__)

# API 키 설정 (환경 변수에서 로드 시도)
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '')

def format_price(price):
    """가격을 보기 좋게 포맷하는 함수"""
    if price is None:
        return "가격 정보 없음"
    
    try:
        if price >= 10000:
            man = price // 10000
            rem = price % 10000
            if rem > 0:
                return f"{man}만 {rem:,}원"
            return f"{man}만원"
        return f"{price:,}원"
    except Exception as e:
        logger.error(f"가격 포맷 오류: {e}")
        return str(price) + "원"

def clean_html(text):
    """HTML 태그 제거 및 특수 문자 변환"""
    if not text:
        return ""
    
    try:
        text = re.sub('<.*?>', '', text)
        text = text.replace('&quot;', '"').replace('&amp;', '&')
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        
        # 반복되는 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        logger.error(f"HTML 정제 오류: {e}")
        return text if text else ""

def extract_price_info(text):
    """텍스트에서 가격 정보 추출"""
    try:
        # 숫자와 쉼표로 구성된 가격 패턴 (예: 12,345원)
        price_pattern = r'(\d{1,3}(?:,\d{3})+|\d+)원'
        prices = []
        
        for match in re.finditer(price_pattern, text):
            price_str = match.group(1).replace(',', '')
            try:
                price = int(price_str)
                prices.append(price)
            except ValueError:
                continue
                
        return prices if prices else None
    except Exception as e:
        logger.error(f"가격 정보 추출 오류: {e}")
        return None

def get_text_similarity(text1, text2):
    """두 텍스트 간의 유사도를 계산"""
    if not text1 or not text2:
        return 0
        
    try:
        # 정제 및 소문자화
        clean_text1 = re.sub(r'[^\w\s]', '', text1.lower())
        clean_text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # SequenceMatcher 사용
        return SequenceMatcher(None, clean_text1, clean_text2).ratio()
    except Exception as e:
        logger.error(f"텍스트 유사도 계산 오류: {e}")
        return 0

def optimize_search_query(query):
    """검색 쿼리를 최적화하는 함수"""
    try:
        # 불필요한 단어 제거
        stop_words = [
            '좀', '추천', '추천해', '추천해줘', '추천해주세요', 
            '찾아줘', '알려줘', '부탁해', '부탁드려요', 
            '최저가', '가장', '제일', '싼', '저렴한', 
            '사고싶어', '구매하고싶어', '없을까', '있을까',
            '얼마', '어떤게', '어떤', '괜찮은'
        ]
        
        query = query.strip()
        query_words = query.split()
        
        # 전체 단어가 1-2개일 경우 그대로 사용
        if len(query_words) <= 2:
            return query
            
        filtered_words = [word for word in query_words if word.lower() not in stop_words]
        
        # 필터링 결과가 없으면 원래 쿼리 사용
        if not filtered_words:
            return query
            
        # 브랜드명과 제품명 사이에 공백 유지
        optimized_query = ' '.join(filtered_words)
        
        # 검색어가 너무 짧아졌으면 원래 쿼리 사용
        if len(optimized_query) < len(query) / 2:
            return query
            
        return optimized_query
    except Exception as e:
        logger.error(f"쿼리 최적화 오류: {e}")
        return query

def are_products_similar(item1, item2):
    """두 상품이 유사한지 판단"""
    try:
        # 제품 ID가 같으면 동일 상품
        if item1.get("productId") and item1.get("productId") == item2.get("productId"):
            return True
            
        # 제목 유사성 검사
        title1 = clean_html(item1.get("title", ""))
        title2 = clean_html(item2.get("title", ""))
        
        # 제목이 매우 짧은 경우 비교하지 않음
        if len(title1) < 5 or len(title2) < 5:
            return False
            
        # 제목 유사도 계산
        title_similarity = get_text_similarity(title1, title2)
        
        # 유사도가 높으면 유사 상품으로 판단
        if title_similarity > 0.85:  # 85% 이상 유사
            return True
            
        # 가격 비교 (10% 이내 차이)
        price1 = item1.get("price", 0)
        price2 = item2.get("price", 0)
        
        if price1 > 0 and price2 > 0:
            price_ratio = min(price1, price2) / max(price1, price2)
            if price_ratio > 0.9 and title_similarity > 0.7:  # 가격 유사하고 제목도 어느 정도 유사
                return True
                
        return False
    except Exception as e:
        logger.error(f"상품 유사성 검사 오류: {e}")
        return False

def fetch_search_results(query, sort_option, price_range=None):
    """네이버 API를 호출하여 검색 결과 가져오기"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encoded_query}&display=40&sort={sort_option}"
        
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            logger.warning(f"네이버 API 응답 오류: {response.status_code}")
            return []
            
        result = response.json()
        items = result.get("items", [])
        
        # 가격 범위 필터링
        if price_range:
            filtered_items = []
            for item in items:
                try:
                    price = int(item.get("lprice", 0))
                    if price_range.get("min") and price < price_range["min"]:
                        continue
                    if price_range.get("max") and price > price_range["max"]:
                        continue
                    filtered_items.append(item)
                except ValueError:
                    continue
            return filtered_items
        return items
    except Exception as e:
        logger.error(f"검색 결과 가져오기 오류: {e}")
        return []

def process_search_item(item):
    """검색 결과 아이템을 처리하여 필요한 정보 추출"""
    try:
        title_clean = clean_html(item.get("title", ""))
        price = int(item.get("lprice", 0))
        
        return {
            "productId": item.get("productId", ""),
            "title": title_clean,
            "price": price,
            "formatted_price": format_price(price),
            "mall_name": item.get("mallName", ""),
            "link": item.get("link", ""),
            "image": item.get("image", ""),
            "category": item.get("category1", ""),
            "brand": item.get("brand", ""),
            "maker": item.get("maker", "")
        }
    except Exception as e:
        logger.error(f"아이템 처리 오류: {e}")
        return None

def search_naver_shopping(query, price_range=None):
    """네이버 쇼핑 검색 메인 함수 - 병렬 처리 및 결과 필터링"""
    start_time = time.time()
    try:
        # 쿼리 최적화
        optimized_query = optimize_search_query(query)
        logger.info(f"검색 쿼리: '{query}' -> '{optimized_query}'")
        
        # 정렬 옵션 설정
        sort_options = ["sim"]  # 기본은 유사도순
        
        # 가격 범위에 따른 정렬 옵션 추가
        if price_range:
            if price_range.get("min") and not price_range.get("max"):
                sort_options = ["asc", "sim"]  # 최소가격 있으면 가격 오름차순 우선
            elif price_range.get("max") and not price_range.get("min"):
                sort_options = ["sim", "date"]  # 최대가격만 있으면 유사도순과 최신순
            elif price_range.get("sort"):
                sort_options = [price_range.get("sort"), "sim"]
        
        # 검색어 변형 준비
        search_queries = [optimized_query]
        
        # 원본 쿼리와 다르면 원본도 포함
        if optimized_query != query:
            search_queries.append(query)
        
        all_items = []
        
        # 병렬로 여러 검색 옵션 실행
        with ThreadPoolExecutor(max_workers=min(len(search_queries) * len(sort_options), 5)) as executor:
            futures = []
            
            for q in search_queries:
                for sort in sort_options:
                    futures.append(executor.submit(fetch_search_results, q, sort, price_range))
            
            # 결과 수집
            for future in futures:
                try:
                    items = future.result()
                    if items:
                        all_items.extend(items)
                except Exception as e:
                    logger.error(f"검색 쓰레드 오류: {e}")
        
        # 중복 제거 및 처리
        unique_items = []
        seen_products = set()
        
        for item in all_items:
            try:
                processed_item = process_search_item(item)
                if not processed_item:
                    continue
                    
                product_id = processed_item.get("productId", "")
                
                # 이미 처리한 상품은 건너뛰기
                if product_id in seen_products:
                    continue
                    
                # 유사 상품 체크
                if any(are_products_similar(processed_item, existing) for existing in unique_items):
                    continue
                    
                seen_products.add(product_id)
                unique_items.append(processed_item)
                
                # 최대 10개 상품만 반환
                if len(unique_items) >= 10:
                    break
            except Exception as e:
                logger.error(f"상품 처리 중 오류: {e}")
        
        # 가격순 정렬
        unique_items.sort(key=lambda x: x.get("price", float('inf')))
        
        end_time = time.time()
        logger.info(f"검색 완료: '{query}' - {len(unique_items)}개 결과, 소요시간: {end_time - start_time:.2f}초")
        
        return unique_items
    except Exception as e:
        logger.error(f"네이버 쇼핑 검색 오류: {e}", exc_info=True)
        return []

def get_item_category(item_title):
    """상품명에서 카테고리를 추출하는 함수"""
    categories = {
        '전자기기': ['스마트폰', '태블릿', '노트북', '컴퓨터', '모니터', 'TV', '이어폰', '헤드폰', '마우스', '키보드'],
        '의류': ['셔츠', '바지', '청바지', '티셔츠', '코트', '자켓', '패딩', '원피스', '스커트', '모자', '양말'],
        '신발': ['운동화', '구두', '슬리퍼', '샌들', '부츠', '로퍼'],
        '가구': ['책상', '의자', '소파', '침대', '매트리스', '책장', '옷장', '서랍'],
        '주방용품': ['냄비', '프라이팬', '그릇', '컵', '칼', '도마', '주전자', '전기밥솥'],
        '화장품': ['스킨', '로션', '크림', '선크림', '파운데이션', '립스틱', '마스카라', '아이섀도우']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in item_title:
                return category
    
    return "기타"