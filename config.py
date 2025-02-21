# config.py
import os
from datetime import timedelta

class Config:
    DEBUG = os.getenv("DEBUG", False)
    TESTING = os.getenv("TESTING", False)
    
    # 시크릿 키 (환경변수에서 불러오거나 기본값 지정)
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    
    # 세션 설정 (Flask 기본)
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # MongoDB 연결 설정 (환경 변수에서 불러오거나 기본값 지정)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://dldndyd:dldndyd@afit-client-db.arouq.mongodb.net/afit-client-db?retryWrites=true&w=majority")
