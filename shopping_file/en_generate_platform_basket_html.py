from functions.utils import format_price
from routes.trans import trans
from flask import url_for

def en_generate_platform_basket_html(basket, format_price, lang):
    platform = basket["platform"]
    items = basket["items"]
    total_price = basket["total_price"]
    
    # 플랫폼 로고 경로를 직접 지정 - 원래 경로 유지
    platform_logos = {
        "쿠팡": "static/images/coupang_logo.png",
        "11번가": "static/images/11st_logo.png",
        "G마켓": "static/images/gmarket_log.png"  # 원래 파일명으로 복원
    }
    
    # 로고 경로 가져오기
    logo_path = platform_logos.get(platform, "static/images/default_logo.png")

    items_html = ""
    for item in items:
        items_html += f"""
        <div class="shopping-basket-item p-4 border-b">
            <a href="{item['link']}" target="_blank" class="flex items-center flex-1">
                <img src="{item['image']}" class="w-16 h-16 object-cover rounded" alt="{item['title']}"/>
                <div class="ml-3 flex-1">
                    <div class="text-sm font-medium">{trans(item['title'],lang)}</div>
                    <div class="text-[#2600FF] font-bold mt-1">{trans(format_price(item['price']),lang)}</div>
                </div>
            </a>
        </div>
        """
    
    return f"""
    <div class="shopping-basket-card bg-white rounded-lg shadow-md">
        <div class="shopping-basket-header p-4 border-b flex flex-col items-start">
            <div class="flex items-center">
                <img src="/{logo_path}" class="h-8 w-auto mr-2" alt="{platform}"/>
                <span class="text-lg font-bold"></span>
            </div>
            <div class="text-sm text-gray-500 mt-1">{trans(f"총 {len(items)}개 상품",lang)}</div>
        </div>
        <div class="shopping-basket-items">
            {items_html}
        </div>
        <div class="p-4 bg-gray-50 flex items-center justify-between rounded-b-lg">
            <span>{trans("총 금액",lang)}</span>
            <span class="text-lg font-bold text-[#2600FF]">{trans(format_price(total_price),lang)}</span>
        </div>
    </div>
    """