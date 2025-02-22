from functions.utils import format_price

def generate_platform_basket_html(basket, format_price):
    platform = basket["platform"]
    items = basket["items"]
    total_price = basket["total_price"]
    
    items_html = ""
    for item in items:
        items_html += f"""
        <div class="shopping-basket-item">
            <a href="{item['link']}" target="_blank" class="flex items-center flex-1">
                <img src="{item['image']}" class="w-16 h-16 object-cover rounded" alt="{item['title']}"/>
                <div class="ml-3 flex-1">
                    <div class="text-sm font-medium">{item['title']}</div>
                    <div class="text-[#2600FF] font-bold mt-1">{format_price(item['price'])}</div>
                </div>
            </a>
        </div>
        """
    
    return f"""
    <div class="shopping-basket-card">
        <div class="shopping-basket-header">
            <div class="text-lg font-bold">{platform}</div>
            <div class="text-sm text-gray-500">총 {len(items)}개 상품</div>
        </div>
        <div class="shopping-basket-items">
            {items_html}
        </div>
        <div class="p-4 bg-gray-50 flex items-center justify-between">
            <span>총 금액</span>
            <span class="text-lg font-bold text-[#2600FF]">{format_price(total_price)}</span>
        </div>
    </div>
    """