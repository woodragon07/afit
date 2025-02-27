# services/db.py
import pymongo
import os

# MongoDB URI를 직접 사용
MONGO_URI = ""

# MongoDB 클라이언트 초기화
client = pymongo.MongoClient(MONGO_URI)

# 데이터베이스 이름 추출 및 연결
db_name = MONGO_URI.split("/")[-1].split("?")[0]
db = client[db_name]

def get_db():
    """MongoDB 데이터베이스 객체 반환"""
    return db