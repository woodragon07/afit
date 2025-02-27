import os
from google.cloud import translate_v2 as translate

# 서비스 계정 JSON 키 파일의 상대 경로 설정
json_key_path = os.path.join(os.path.dirname(__file__), "vsssssa12-10b7b37d563d.json")
translator = translate.Client.from_service_account_json(json_key_path)

def detect_language(text):
    """Google Cloud Translation API를 사용하여 언어 감지"""
    try:
        result = translator.detect_language(text)
        return result["language"]  # 감지된 언어 코드 반환
    except Exception as e:
        print(f"언어 감지 오류: {e}")
        return "ko"  # 감지 실패 시 기본값 'ko'

def transKO(text):
    """입력된 텍스트를 감지하여 한국어로 번역"""
    detected_lang = detect_language(text)
    try:
        translated_text = translator.translate(text, target_language='ko')['translatedText']
        return translated_text, detected_lang
    except Exception as e:
        print(f"번역 오류: {e}")
        return text, detected_lang  # 오류 발생 시 원본 텍스트 반환

def trans(text, source_lang):
    """입력된 텍스트를 지정된 언어로 번역"""
    try:
        translated_text = translator.translate(text, target_language=source_lang)['translatedText']
        return translated_text
    except Exception as e:
        print(f"번역 오류: {e}")
        return text  # 오류 발생 시 원본 텍스트 반환
