## utils.py (공통 함수 파일)
import re
import urllib.parse
import requests

NAVER_CLIENT_ID = 'sVLg7QDsZXmBjyWgunV5'
NAVER_CLIENT_SECRET = '9_KNpe6xDN'

def format_price(price):
    """가격을 보기 좋게 포맷하는 함수"""
    try:
        if price >= 10000:
            man = price // 10000
            rem = price % 10000
            if rem > 0:
                return f"{man}만 {rem:,}원"
            return f"{man}만원"
        return f"{price:,}원"
    except:
        return str(price) + "원"

def clean_html(text):
    """HTML 태그 제거 및 특수 문자 변환"""
    text = re.sub('<.*?>', '', text)
    text = text.replace('&quot;', '"').replace('&amp;', '&')
    return text

def search_naver_shopping(query, price_range=None):
    """네이버 쇼핑 API를 호출하여 검색 결과 반환"""
    try:
        sort_option = "sim"
        if price_range and price_range.get("sort") == "price_asc":
            sort_option = "asc"
        url = f"https://openapi.naver.com/v1/search/shop.json?query={urllib.parse.quote(query)}&display=20&sort={sort_option}"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return []
        items = resp.json().get("items", [])
        
        filtered = []
        for it in items:
            try:
                price = int(it["lprice"])
                # 가격대 필터 적용
                if price_range:
                    if price_range.get("min") and price < price_range["min"]:
                        continue
                    if price_range.get("max") and price > price_range["max"]:
                        continue
                title_clean = clean_html(it["title"])
                # 중복 제거
                if not any(clean_html(x["title"]) == title_clean for x in filtered):
                    it["price"] = price
                    it["formatted_price"] = format_price(price)
                    it["title"] = title_clean
                    it["mall_name"] = it.get("mallName", "")
                    it["link"] = it["link"]
                    it["image"] = it["image"]
                    filtered.append(it)
            except:
                pass
        return filtered
    except:
        return []