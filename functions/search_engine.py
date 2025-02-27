# functions/search_engine.py - 검색 관련 함수
import logging
from functions.common_logger import get_logger
from functions.utils import search_naver_shopping

# 모듈 로거 가져오기
logger = get_logger(__name__)

def get_lowest_price_items(keywords, specific_product=None, brand=None, attributes=None):
    """키워드로 최저가 상품을 검색하는 함수"""
    logger.info(f"최저가 검색 시작: 키워드={keywords}, 특정제품={specific_product}, 브랜드={brand}")
    
    try:
        all_items = []
        
        # 속성을 키워드에 추가하여 검색 정확도 향상
        search_keywords = keywords.copy() if keywords else []
        
        # 특정 제품 처리
        if specific_product and specific_product not in search_keywords:
            search_keywords.append(specific_product)
        
        # 브랜드 처리
        if brand:
            brand_keywords = [f"{brand} {kw}" for kw in search_keywords if brand.lower() not in kw.lower()]
            search_keywords.extend(brand_keywords)
        
        # 속성 처리
        if attributes and isinstance(attributes, list):
            attr_keywords = []
            for attr in attributes:
                for kw in search_keywords:
                    if attr.lower() not in kw.lower():
                        attr_keywords.append(f"{kw} {attr}")
            search_keywords.extend(attr_keywords)
        
        # 중복 제거 및 길이순 정렬 (더 구체적인 키워드 우선)
        search_keywords = list(set(search_keywords))
        search_keywords.sort(key=len, reverse=True)
        
        logger.info(f"확장된 검색 키워드: {search_keywords}")
        
        # 다양한 키워드로 검색 시도
        for kw in search_keywords[:5]:  # 최대 5개 키워드만 사용
            logger.debug(f"최저가 검색 키워드: {kw}")
            items = search_naver_shopping(kw, {"sort": "asc"})  # 가격 오름차순 정렬
            if items:
                all_items.extend(items)
                logger.debug(f"최저가 검색 결과: {len(items)}개 찾음")
        
        # 중복 제거 및 가격 순 정렬
        unique_items = []
        seen_ids = set()
        
        for item in sorted(all_items, key=lambda x: x.get("price", float('inf'))):
            item_id = item.get("productId")
            if item_id and item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_items.append(item)
        
        logger.info(f"최저가 검색 완료: {len(unique_items)}개 결과")
        return unique_items[:10]  # 상위 10개 상품만 반환
        
    except Exception as e:
        logger.error(f"최저가 검색 오류: {e}", exc_info=True)
        return []