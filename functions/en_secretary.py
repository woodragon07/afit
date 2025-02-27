import re
import json
import google.generativeai as genai
from functions.utils import search_naver_shopping, format_price
from shopping_file.parse_shopping_request_with_llm import parse_shopping_request_with_llm
from shopping_file.en_generate_platform_basket_html import en_generate_platform_basket_html

def search_platform_items(platform, item_name, price_limit, lang):
    try:
        items = search_naver_shopping(
            f"{platform} {item_name}", 
            {"max": price_limit} if price_limit else None
        ) or []
        
        platform_keywords = {
            "11번가": ["11번가", "11ST", "11STREET"],
            "G마켓": ["G마켓", "지마켓", "GMARKET"],
            "쿠팡": ["쿠팡", "COUPANG"]
        }
        
        keywords = platform_keywords.get(platform, [platform])
        platform_items = [
            item for item in items 
            if any(kw.lower() in item["mall_name"].lower() for kw in keywords)
        ]
        
        return platform_items[:1] if platform_items else []
    except Exception as e:
        print(f"{platform} 검색 오류:", e)
        return []

def handle_shopping_secretary_mode(user_message, search_naver_shopping_func, format_price_func):  # 매개변수 수정
    try:
        # 1. LLM으로 필요한 품목 분석
        parsed = parse_shopping_request_with_llm(user_message)
        items = parsed.get("items", [])
        price_limit = parsed.get("price_limit")
        
        if not items:
            return [{"response": "필요한 품목을 파악하지 못했습니다."}]
            
        # 2. 초기 응답
        responses = [{"response": f"필요한 품목을 찾았습니다: {', '.join(items)}"}]
        
        # 3. 플랫폼별 검색
        platforms = ["G마켓", "11번가", "쿠팡"]
        valid_baskets = []  
        
        for platform in platforms:
            basket_items = []
            total_price = 0
            
            for item in items:
                found_items = search_platform_items(platform, item, price_limit, 'ko')
                if found_items:
                    sorted_items = sorted(found_items, key=lambda x: x["price"])
                    item_info = sorted_items[0]
                    
                    if price_limit is None or total_price + item_info["price"] <= price_limit:
                        basket_items.append(item_info)
                        total_price += item_info["price"]
            
            if len(basket_items) == len(items) and (price_limit is None or total_price <= price_limit):
                basket = {
                    "platform": platform,
                    "items": basket_items,
                    "total_price": total_price
                }
                valid_baskets.append(basket)
        
        if valid_baskets:
            valid_baskets.sort(key=lambda x: x["total_price"])
            all_baskets_html = ""
            for basket in valid_baskets:
                all_baskets_html += generate_platform_basket_html(basket, format_price_func)  # format_price_func 사용
                
            responses.append({
                "response": f"""
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
                    {all_baskets_html}
                </div>
                """,
                "html": True
            })
        else:
            responses.append({
                "response": f"죄송합니다. {format_price_func(price_limit) if price_limit else ''} 이내로 모든 상품을 찾지 못했습니다."  # format_price_func 사용
            })
            
        return responses
        
    except Exception as e:
        print("쇼핑비서 모드 오류:", e)
        return [{"response": "처리 중 오류가 발생했습니다."}]
    
def handle_en_shopping_secretary_mode(user_message, search_naver_shopping_func, format_price_func,lang):  # 매개변수 수정
    from routes.trans import trans
    try:
        # 1. LLM으로 필요한 품목 분석
        parsed = parse_shopping_request_with_llm(user_message)
        items = parsed.get("items", [])
        price_limit = parsed.get("price_limit")
        
        if not items:
            return [{"response": trans("필요한 품목을 파악하지 못했습니다.",lang)}]
            
        # 2. 초기 응답
        responses = [{"response": trans(f"필요한 품목을 찾았습니다: {', '.join(items)}",lang)}]
        
        # 3. 플랫폼별 검색
        platforms = ["G마켓", "11번가", "쿠팡"]
        valid_baskets = []  
        
        for platform in platforms:
            basket_items = []
            total_price = 0
            
            for item in items:
                found_items = search_platform_items(platform, item, price_limit, 'ko')
                if found_items:
                    sorted_items = sorted(found_items, key=lambda x: x["price"])
                    item_info = sorted_items[0]
                    
                    if price_limit is None or total_price + item_info["price"] <= price_limit:
                        basket_items.append(item_info)
                        total_price += item_info["price"]
            
            if len(basket_items) == len(items) and (price_limit is None or total_price <= price_limit):
                basket = {
                    "platform": platform,
                    "items": basket_items,
                    "total_price": total_price
                }
                valid_baskets.append(basket)
        
        if valid_baskets:
            valid_baskets.sort(key=lambda x: x["total_price"])
            all_baskets_html = ""
            for basket in valid_baskets:
                all_baskets_html += en_generate_platform_basket_html(basket, format_price_func,lang)  # format_price_func 사용
                
            responses.append({
                "response": f"""
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
                    {all_baskets_html}
                </div>
                """,
                "html": True
            })
        else:
            responses.append({
                "response": trans(f"죄송합니다. {format_price_func(price_limit) if price_limit else ''} 이내로 모든 상품을 찾지 못했습니다.",lang)  # format_price_func 사용
            })
            
        return responses
        
    except Exception as e:
        print("쇼핑비서 모드 오류:", e)
        return [{"response": "처리 중 오류가 발생했습니다."}]