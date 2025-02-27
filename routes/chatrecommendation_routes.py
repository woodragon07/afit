# routes/chatrecommendation_routes.py - 채팅/추천 관련 라우트를 담당
import logging
from flask import Blueprint, request, jsonify
import google.generativeai as genai

# 각 모듈에서 필요한 함수 임포트
from functions.common_logger import get_logger
from functions.utils import search_naver_shopping, format_price, clean_html
from functions.price_analyzer import extract_price_range
from functions.gemini_ai import analyze_user_intent_with_gemini, get_non_shopping_response
from functions.search_engine import get_lowest_price_items

# 모듈 로거 가져오기
logger = get_logger(__name__)

bp = Blueprint('chatrecommendation', __name__)

@bp.route("/chat", methods=["POST"])
def chat():
    """채팅 기반 상품 추천 API 라우트"""
    data = request.json
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "helper")
    
    if not user_message:
        return jsonify([{"response": "메시지를 입력하세요."}])
    
    if mode == "helper":
        try:
            logger.info(f"사용자 메시지: {user_message}")
            
            # Gemini로 사용자 의도 분석
            intent_analysis = analyze_user_intent_with_gemini(user_message)
            logger.info(f"의도 분석 결과: {intent_analysis}")
            
            # 쇼핑 요청이 아니면 일반 대화 응답 제공
            if not intent_analysis.get("is_shopping_request", False):
                logger.info("쇼핑 요청이 아님, 일반 대화 응답 제공")
                general_response = get_non_shopping_response(user_message)
                return jsonify([{"response": general_response}])
            
            # 검색 준비
            keywords = intent_analysis.get("product_keywords", [])
            if not keywords:
                logger.warning("키워드를 찾지 못함, 원본 메시지를 키워드로 사용")
                keywords = [user_message]
                
            # 정규식으로도 가격대 추출 (백업)
            regex_price_range = extract_price_range(user_message)
            if regex_price_range:
                logger.info(f"정규식으로 가격 범위 추출: {regex_price_range}")
            
            # 가격 범위 설정 (Gemini 또는 정규식)
            price_range = None
            if intent_analysis.get("price_min") is not None or intent_analysis.get("price_max") is not None:
                price_range = {}
                if intent_analysis.get("price_min") is not None:
                    price_range["min"] = intent_analysis["price_min"]
                if intent_analysis.get("price_max") is not None:
                    price_range["max"] = intent_analysis["price_max"]
                logger.info(f"Gemini 가격 범위: {price_range}")
            elif regex_price_range:
                price_range = regex_price_range
                logger.info(f"정규식 가격 범위 사용: {price_range}")
            
            responses = []
            found_items = []
            
            # 최저가 요청 처리
            if intent_analysis.get("request_type") == "lowest_price":
                logger.info("최저가 검색 요청 처리")
                # 검색 시작 알림
                responses.append({"response": f"🔍 '{', '.join(keywords)}' 최저가 검색 중..."})
                
                # 최저가 상품 검색
                found_items = get_lowest_price_items(
                    keywords, 
                    intent_analysis.get("specific_product"), 
                    intent_analysis.get("brand_preference"),
                    intent_analysis.get("attributes", [])
                )
                
                if found_items:
                    # 최저가 상품 정보 표시
                    top_item = found_items[0]
                    responses[0] = {"response": f"💰 '{', '.join(keywords)}' 최저가: {top_item['formatted_price']} ({top_item.get('mall_name', '판매처 정보 없음')})"}
                    logger.info(f"최저가 상품 찾음: {top_item['title']} - {top_item['formatted_price']}")
                else:
                    responses[0] = {"response": f"😅 '{', '.join(keywords)}'에 대한 최저가 정보를 찾지 못했어요."}
                    logger.warning(f"최저가 상품을 찾지 못함: {keywords}")
            else:
                # 일반 검색 알림
                logger.info("일반 상품 검색 요청 처리")
                responses.append({"response": f"🔍 '{', '.join(keywords)}' 검색 중..."})
            
            # 일반 검색 또는 최저가 검색에서 찾은 상품이 없는 경우 추가 검색
            if not found_items:
                logger.info("추가 검색 시도")
                for kw in keywords:
                    items = search_naver_shopping(kw, price_range)
                    if items:
                        found_items.extend(items)
                        logger.info(f"키워드 '{kw}'로 {len(items)}개 상품 찾음")
            
            # 검색 결과가 있으면 상품 카드 표시
            if found_items:
                logger.info(f"총 {len(found_items)}개 상품 찾음")
                # 가격순 정렬
                found_items.sort(key=lambda x: x.get("price", float('inf')))
                
                for it in found_items:
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
                            <img src="{it['image']}" alt="{it['title']}" class="product-image"/>
                        </div>
                        <div class="product-info">
                            <div class="product-meta">{it.get('mall_name','판매처 정보 없음')}</div>
                            <h3 class="product-title">{it['title']}</h3>
                            <div class="product-price">{it['formatted_price']}</div>
                            <div class="product-recommendation">추천 상품</div>
                            <div class="mt-4">
                                <a href="{it['link']}" target="_blank"
                                   class="block w-full text-center bg-[#4054E5] hover:bg-[#3047C9] text-white py-2 px-4 rounded-md transition-colors">
                                   제품 보기
                                </a>
                            </div>
                        </div>
                    </div>
                    """
                    responses.append({"response": product_html, "html": True})
                
                # 일반 검색인 경우에만 가격 범위 요약 추가
                if intent_analysis.get("request_type") != "lowest_price":
                    minp = min(x.get("price", float('inf')) for x in found_items)
                    maxp = max(x.get("price", 0) for x in found_items)
                    
                    # 가격 범위 정보 텍스트
                    price_text = ""
                    if price_range:
                        if price_range.get("min") and price_range.get("max"):
                            price_text = f" (검색 범위: {format_price(price_range['min'])}~{format_price(price_range['max'])})"
                        elif price_range.get("min"):
                            price_text = f" (검색 범위: {format_price(price_range['min'])} 이상)"
                        elif price_range.get("max"):
                            price_text = f" (검색 범위: {format_price(price_range['max'])} 이하)"
                    
                    summary = f"💡 '{', '.join(keywords)}' 검색 결과: {format_price(minp)}~{format_price(maxp)}{price_text}"
                    responses[0] = {"response": summary}
                    logger.info(f"검색 결과 요약: {minp}~{maxp}원, {len(found_items)}개 상품")
            else:
                # 상품을 찾지 못한 경우
                logger.warning(f"상품을 찾지 못함: {keywords}")
                responses[0] = {"response": f"😅 '{', '.join(keywords)}'에 대한 상품을 찾지 못했어요."}
                
                # 검색어 제안 추가
                try:
                    logger.info("대체 검색어 제안 시도")
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    prompt = f"""
                    사용자가 '{', '.join(keywords)}'에 대한 상품을 찾으려고 했지만 결과가 없습니다.
                    비슷한 의미를 가지는 다른 검색어를 2-3개만 제안해주세요. 
                    간결하게 대안만 나열해 주세요.
                    """
                    suggestion = model.generate_content(prompt).text
                    responses.append({"response": f"다음 검색어로 시도해보세요: {suggestion}"})
                    logger.info(f"대체 검색어 제안: {suggestion}")
                except Exception as e:
                    logger.error(f"검색어 제안 오류: {e}")
                
            return jsonify(responses)
        except Exception as e:
            logger.error(f"도우미 모드 오류: {e}", exc_info=True)
            return jsonify([{"response": "검색 처리 중 오류가 발생했습니다."}])
    
    elif mode == "shopping":
        try:
            logger.info("쇼핑 모드 요청")
            from functions.secretary import handle_shopping_secretary_mode
            responses = handle_shopping_secretary_mode(user_message, search_naver_shopping, format_price)
            return jsonify(responses)
        except Exception as e:
            logger.error(f"쇼핑 모드 오류: {e}", exc_info=True)
            return jsonify([{"response": "쇼핑 처리 중 오류가 발생했습니다."}])
    else:
        logger.warning(f"지원하지 않는 모드: {mode}")
        return jsonify([{"response": "지원하지 않는 모드입니다."}])