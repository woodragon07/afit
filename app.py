# app.py Flask 앱 팩토리 및 Blueprint 등록, 앱 실행
import os
from datetime import timedelta
from dotenv import load_dotenv
import config
import google.generativeai as genai
from flask import Flask
# from utils.error_handler import register_error_handlers

# Blueprint 임포트
from routes import auth_routes, product_routes, bookmark_routes, chatrecommendation_routes

# 확장 모듈 임포트 (extensions.py에 정의)
from extensions import mongo

def create_app():
    app = Flask(__name__)
    
    # 기본 설정 로드
    app.config.from_object(config.Config)
    
    # 환경 변수 로딩 및 API 키 설정
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    
    print("Google API Key:", GOOGLE_API_KEY)
    print("Naver Client ID:", NAVER_CLIENT_ID)
    print("Naver Client Secret:", NAVER_CLIENT_SECRET)
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 세션 설정
    app.secret_key = 'your_secret_key'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    
    # MongoDB Atlas 연결 설정
    app.config["MONGO_URI"] = "mongodb+srv://dldndyd:dldndyd@afit-client-db.arouq.mongodb.net/afit-client-db?retryWrites=true&w=majority"
    
    # 확장 모듈 초기화
    mongo.init_app(app)
    
    # Blueprint 등록
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(product_routes.bp)
    app.register_blueprint(bookmark_routes.bp)
    app.register_blueprint(chatrecommendation_routes.bp)
    
    # 에러 핸들러 등록
    # register_error_handlers(app)
    
    # 앱 시작 시 데이터베이스 테이블 생성 로직 (필요 시)
    with app.app_context():
        try:
            print("데이터베이스 테이블이 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"데이터베이스 테이블 생성 중 오류 발생: {str(e)}")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
