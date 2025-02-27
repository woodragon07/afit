from functions.utils import search_naver_shopping, format_price  # utils에서 가져옴 네이버 쇼핑서치,가격출력력

def search_platform_items(platform, item_name, price_limit, search_naver_shopping):
    try:
        items = search_naver_shopping(
            f"{platform} {item_name}", 
            {"max": price_limit} if price_limit else None
        )
        
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