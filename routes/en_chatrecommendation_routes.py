# routes/recommendation_routes.py 채팅/추천 관련 라우트를 담당
import re
from flask import Blueprint, request, jsonify
from functions.utils import search_naver_shopping, format_price
from .trans import transKO,trans
bp = Blueprint('en_chatrecommendation', __name__)

def extract_price_range(text):
    try:
        match = re.search(r'(\d+)만원대', text)
        if match:
            base = int(match.group(1))
            return {"min": base * 10000, "max": (base + 10) * 10000 - 1, "display": f"{base}만원대"}
        return None
    except:
        return None

@bp.route("/ENchat", methods=["POST"])
def ENchat():
    data = request.json
    
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "helper")

    lang= transKO(user_message)[1]
    user_message=transKO(user_message)[0]
    
    if not user_message:
        return jsonify([{"response": "메시지를 입력하세요"}])

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
                                    title: '{it['title'].replace("'", "'")}',
                                    price: '{it['formatted_price']}',
                                    mall_name: '{it.get('mall_name', '').replace("'", "'")}',
                                    image_url: '{it['image']}',
                                    product_url: '{it['link']}'
                                }})">
                            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </button>
                        <div class="product-image-container">
                            <img src="{it['image']}" alt="{trans(it['title'],lang)}" class="product-image"/>
                        </div>
                        <div class="product-info">
                            <div class="product-meta">{trans(it.get('mall_name','판매처 정보 없음'),lang)}</div>
                            <h3 class="product-title">{trans(it['title'],lang)}</h3>
                            <div class="product-price">{trans(it['formatted_price'],lang)}</div>
                            <div class="product-recommendation">{trans('추천 상품',lang)}</div>
                            <div class="mt-4">
                                <a href="{it['link']}" target="_blank"
                                   class="block w-full text-center bg-[#4054E5] hover:bg-[#3047C9] text-white py-2 px-4 rounded-md transition-colors">
                                   {trans('제품 보기',lang)}
                                </a>
                            </div>
                        </div>
                    </div>
                    """
                    responses.append({"response": product_html, "html": True})
        if found_items:
            minp = min(x["price"] for x in found_items)
            maxp = max(x["price"] for x in found_items)
            summary = trans(f"💡{format_price(minp)}~{format_price(maxp)} 범위의 상품을 찾았어요.",lang)
            responses.insert(0, {"response": summary})
        else:
            responses.append({"response": trans("😅 조건에 맞는 상품을 찾지 못했어요.",lang)})
        return jsonify(responses)
    
    elif mode == "shopping":
        from functions.en_secretary import handle_en_shopping_secretary_mode
        responses = handle_en_shopping_secretary_mode(user_message, search_naver_shopping, format_price,lang)
        return jsonify(responses)
    else:
        return jsonify([{"response": trans("지원하지 않는 모드입니다.",lang)}])