import google.generativeai as genai
import json

def clean_response(raw):
    # 코드 블록 제거: 응답에 ```가 포함된 경우 제거
    if raw.startswith("```"):
        # 첫 번째 줄과 마지막 줄 제거
        lines = raw.splitlines()
        # 만약 첫 번째 줄이 ```json 혹은 ```로 시작한다면, 제거
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return raw.strip()

def parse_shopping_request_with_llm(user_message):  
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        사용자의 요청을 분석해 필요한 품목 리스트와 가격 제한을 추출하세요.
        결과는 아래 형식의 JSON으로만 반환하세요. 추가 설명은 하지 마세요.
        {{
          "items": ["필요한 품목1", "필요한 품목2", ...],
          "price_limit": 가격제한 (없으면 null)
        }}
        
        예시1) 
        입력: "김치찌개 재료가 필요해"
        출력: {{"items": ["김치", "돼지고기", "두부", "대파", "마늘", "고춧가루"], "price_limit": null}}
        
        예시2)
        입력: "겨울철 스키장 룩을 50만원 내로 맞추고 싶어"
        출력: {{"items": ["스키복", "스키바지", "스키장갑", "스키고글", "방한내의"], "price_limit": 500000}}
        
        실제 입력: {user_message}
        """
        resp = model.generate_content(prompt)
        raw_result = resp.text
        print("Raw response:", raw_result)
        
        # 코드 블록 제거
        cleaned_result = clean_response(raw_result)
        print("Cleaned response:", cleaned_result)
        
        return json.loads(cleaned_result)
    except Exception as e:
        print("LLM 분석 오류:", e)
        return {"items": [], "price_limit": None}