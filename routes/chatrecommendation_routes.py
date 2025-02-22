# routes/recommendation_routes.py 채팅/추천 관련 라우트를 담당
import re
from flask import Blueprint, request, jsonify
from functions.utils import search_naver_shopping, format_price


bp = Blueprint('recommendation', __name__)

def extract_price_range(text):
    try:
        match = re.search(r'(\d+)만원대', text)
        if match:
            base = int(match.group(1))
            return {"min": base * 10000, "max": (base + 10) * 10000 - 1, "display": f"{base}만원대"}
        return None
    except:
        return None

@bp.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "helper")
    
    if not user_message:
        return jsonify([{"response": "메시지를 입력하세요."}])
    
    if mode == "helper":
        price_range = extract_price_range(user_message)
        keywords = [user_message]
        found_items = []
        responses = []
        for kw in keywords:
            items = search_naver_shopping(kw, price_range)
            if items:
                found_items.extend(items)
                for it in items:
                    product_html = f"""
                    <div class="product-card">
                        <button type="button" class="bookmark-btn" id="bookmark-{it.get('productId', '')}"
                                onclick="toggleBookmark({{
                                    item_id: '{it.get('productId', '')}',
                                    title: '{it['title'].replace("'", "\\'")}',
                                    price: '{it['formatted_price']}',
                                    mall_name: '{it.get('mall_name', '').replace("'", "\\'")}',
                                    image_url: '{it['image']}',
                                    product_url: '{it['link']}'
                                }})">
                            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </button>
                        <div class="product-image-container">
                            <img src="{it['image']}" alt="{it['title']}" class="product-image"/>
                        </div>
                        <div class="product-info">
                            <div class="product-meta">{it.get('mall_name','판매처 정보 없음')}</div>
                            <h3 class="product-title">{it['title']}</h3>
                            <div class="product-price">{it['formatted_price']}</div>
                            <div class="product-recommendation">추천 상품</div>
                            <div class="mt-4">
                                <a href="{it['link']}" target="_blank"
<<<<<<< HEAD
                                   class="block w-full text-center bg-[#2600FF] hover:bg-[#2600FF] text-white py-2 px-4 rounded-md transition-colors">
=======
                                   class="block w-full text-center bg-[#FF9999] hover:bg-[#FF6B6B] text-white py-2 px-4 rounded-md transition-colors">
>>>>>>> 8592ca44a16150c7cbfcb58f7ebb14d6ca4741ff
                                   제품 보기
                                </a>
                            </div>
                        </div>
                    </div>
                    """
                    responses.append({"response": product_html, "html": True})
        if found_items:
            minp = min(x["price"] for x in found_items)
            maxp = max(x["price"] for x in found_items)
            summary = f"💡 {format_price(minp)}~{format_price(maxp)} 범위의 상품을 찾았어요."
            responses.insert(0, {"response": summary})
        else:
            responses.append({"response": "😅 조건에 맞는 상품을 찾지 못했어요."})
        return jsonify(responses)
    
    elif mode == "shopping":
        from functions.secretary import handle_shopping_secretary_mode
        responses = handle_shopping_secretary_mode(user_message, search_naver_shopping, format_price)
        return jsonify(responses)
    else:
        return jsonify([{"response": "지원하지 않는 모드입니다."}])