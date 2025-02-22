import re
import json
import google.generativeai as genai
from functions.utils import search_naver_shopping, format_price  # utils에서 가져옴 네이버 쇼핑서치,가격출력력
from shopping_file.parse_shopping_request_with_llm import parse_shopping_request_with_llm
from shopping_file.generate_platform_basket_html import generate_platform_basket_html
from shopping_file.search_platform_items import search_platform_items

def handle_shopping_secretary_mode(user_message, search_naver_shopping, format_price):
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
                found_items = search_platform_items(platform, item, price_limit, search_naver_shopping)
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
                all_baskets_html += generate_platform_basket_html(basket, format_price)
                
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
                "response": f"죄송합니다. {format_price(price_limit) if price_limit else ''} 이내로 모든 상품을 찾지 못했습니다."
            })
            
        return responses
        
    except Exception as e:
        print("쇼핑비서 모드 오류:", e)
        return [{"response": "처리 중 오류가 발생했습니다."}]


