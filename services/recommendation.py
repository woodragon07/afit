# services/recommendation.py
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pinecone import Pinecone, ServerlessSpec
import uuid
import json
from functools import lru_cache
from dotenv import load_dotenv
import pymongo

load_dotenv()  # .env 파일의 내용이 os.environ에 로드됩니다.

# 앱에서 사용하는 MongoDB URI 직접 사용
MONGO_URI = ""
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

client = pymongo.MongoClient(MONGO_URI)
db = client["afit-client-db"]  # 실제 DB 이름으로 변경



# MongoDB 연결 및 기존 API 함수 임포트
from .db import db  # get_db 대신 db 객체를 직접 가져옴
from functions.utils import search_naver_shopping, clean_html

class RecommendationService:
    def __init__(self, num_clusters=3):
        """추천 서비스 초기화"""
        self.num_clusters = num_clusters
        
        # OpenAI API 설정
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
        
        # Pinecone 설정 및 초기화
        self.pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        self.pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")
        
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Pinecone 인덱스가 존재하는지 확인하고 없으면 생성
        self._initialize_pinecone()
        
        # 인덱스 연결
        self.index = self.pc.Index(self.pinecone_index_name)
        
    def _initialize_pinecone(self):
        """Pinecone 인덱스 초기화"""
        # 기존 인덱스 목록 가져오기
        indexes = self.pc.list_indexes()
        
        # 인덱스가 이미 존재하면 건너뜁니다.
        if self.pinecone_index_name in indexes:
            print(f"Pinecone 인덱스 '{self.pinecone_index_name}' 이미 존재함. 생성 건너뜀.")
            return
        
        # 인덱스가 없으면 생성 시도
        try:
            # OpenAI embedding 차원은 1536 (text-embedding-3-small)
            self.pc.create_index(
                name=self.pinecone_index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"Pinecone 인덱스 '{self.pinecone_index_name}' 생성됨")
        except Exception as e:
            if "ALREADY_EXISTS" in str(e):
                print(f"Pinecone 인덱스 '{self.pinecone_index_name}' 이미 존재함 (예외 처리됨).")
            else:
                raise

    
    def _get_mongodb_connection(self):
        """MongoDB 연결 가져오기"""
        try:
            mongo_uri = current_app.config["MONGO_URI"]
        except RuntimeError:
            # Flask 애플리케이션 컨텍스트 밖에서 실행될 때
            mongo_uri = os.environ.get("MONGO_URI")
            
        client = pymongo.MongoClient(mongo_uri)
        db_name = mongo_uri.split("/")[-1].split("?")[0]
        return client[db_name]

    def get_user_bookmarks(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 북마크 데이터를 MongoDB에서 가져오기"""
        bookmarks = list(db.product_bookmark.find({"user_id": user_id}))
        return bookmarks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """텍스트 리스트를 임베딩 벡터로 변환"""
        if not texts:
            return []
            
        try:
            response = openai.embeddings.create(
                model="",
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"임베딩 생성 중 오류: {str(e)}")
            # 오류 시 빈 임베딩 반환
            return [[0] * 1536] * len(texts)
    
    def store_product_embeddings(self, products: List[Dict[str, Any]]) -> bool:
        """상품 데이터와 임베딩을 Pinecone에 저장"""
        if not products:
            return False
            
        # 상품 제목 및 설명 추출
        product_texts = []
        for product in products:
            title = product.get("title", "")
            # 설명이 있다면 함께 사용
            description = product.get("description", "")
            # 타이틀과 설명을 결합하여 더 풍부한 임베딩 생성
            text = f"{title} {description}".strip()
            product_texts.append(text)
        
        # 임베딩 생성
        embeddings = self.generate_embeddings(product_texts)
        
        # Pinecone에 저장할 벡터 데이터 준비
        vectors_to_upsert = []
        
        for i, (product, embedding) in enumerate(zip(products, embeddings)):
            # 상품 ID가 없으면 UUID 생성
            product_id = product.get("item_id") or str(uuid.uuid4())
            
            # 메타데이터 준비 (검색 결과에 필요한 정보)
            metadata = {
                "item_id": product.get("item_id", ""),
                "title": product.get("title", ""),
                "price": product.get("price", ""),
                "mall_name": product.get("mall_name", ""),
                "product_url": product.get("product_url", ""),
                "image_url": product.get("image_url", ""),
                "timestamp": datetime.now().isoformat()
            }
            
            # Pinecone 벡터 데이터 구조 생성
            vector_data = {
                "id": product_id,
                "values": embedding,
                "metadata": metadata
            }
            
            vectors_to_upsert.append(vector_data)
        
        # 벡터 데이터를 Pinecone에 업서트
        try:
            self.index.upsert(vectors=vectors_to_upsert)
            return True
        except Exception as e:
            print(f"Pinecone 저장 중 오류: {str(e)}")
            return False
    
    def find_similar_products(self, embedding: List[float], top_k: int = 10, 
                             exclude_ids: List[str] = None) -> List[Dict[str, Any]]:
        """임베딩 벡터와 유사한 상품 검색"""
        if exclude_ids is None:
            exclude_ids = []
            
        try:
            # Pinecone 유사도 검색
            query_result = self.index.query(
                vector=embedding,
                top_k=top_k + len(exclude_ids),  # 제외 상품을 고려해 더 많이 가져옴
                include_metadata=True
            )
            
            # 검색 결과 처리
            results = []
            for match in query_result['matches']:
                # 제외할 ID 목록에 없는 경우만 추가
                if match['id'] not in exclude_ids:
                    results.append({
                        "item_id": match['metadata'].get('item_id'),
                        "title": match['metadata'].get('title'),
                        "price": match['metadata'].get('price'),
                        "mall_name": match['metadata'].get('mall_name'),
                        "product_url": match['metadata'].get('product_url'),
                        "image_url": match['metadata'].get('image_url'),
                        "similarity_score": match['score']
                    })
                
                # 목표 개수에 도달하면 중단
                if len(results) >= top_k:
                    break
                    
            return results
        except Exception as e:
            print(f"Pinecone 검색 중 오류: {str(e)}")
            return []
    
    def cluster_bookmarks(self, bookmarks: List[Dict]) -> Tuple[List[str], List[List[float]]]:
        """북마크를 클러스터링하여 관심사 그룹화 및 검색 쿼리 생성"""
        if not bookmarks:
            return [], []
            
        # 북마크에서 상품 제목 추출
        product_titles = [bookmark.get("title", "") for bookmark in bookmarks]
        
        # 제목에서 따옴표 및 HTML 태그 제거
        clean_titles = [clean_html(title) for title in product_titles]
        
        # 상품 제목 임베딩
        embeddings = self.generate_embeddings(clean_titles)
        
        # 클러스터링 실행
        cluster_result = self._perform_clustering(embeddings)
        
        # 클러스터별 검색 쿼리 생성
        queries = self._generate_queries(bookmarks, cluster_result, embeddings)
        
        # 클러스터 중심점 반환 (Pinecone 검색용)
        centers = cluster_result["centers"]
        
        return queries, centers
    
    def _perform_clustering(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """임베딩 벡터 클러스터링"""
        if not embeddings:
            return {"labels": [], "centers": [], "cluster_sizes": {}}
            
        n_samples = len(embeddings)
        
        # 북마크 수에 따라 클러스터 수 조정
        n_clusters = min(self.num_clusters, max(1, n_samples - 1))
            
        if n_clusters <= 1:
            # 클러스터링할 필요 없이 하나의 중심점만 사용
            center = np.mean(embeddings, axis=0)
            return {
                "labels": [0] * n_samples,
                "centers": [center.tolist()],
                "cluster_sizes": {0: n_samples}
            }
        
        # KMeans 클러스터링 실행
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        centers = kmeans.cluster_centers_
        
        # 클러스터별 크기 계산
        cluster_sizes = {}
        for label in labels:
            if label in cluster_sizes:
                cluster_sizes[label] += 1
            else:
                cluster_sizes[label] = 1
        
        return {
            "labels": labels,
            "centers": centers.tolist(),
            "cluster_sizes": cluster_sizes
        }
    
    def _generate_queries(self, bookmarks: List[Dict], cluster_result: Dict[str, Any], 
                          embeddings: List[List[float]]) -> List[str]:
        """각 클러스터에서 검색 쿼리 생성"""
        if not bookmarks:
            return []
            
        labels = cluster_result["labels"]
        centers = cluster_result["centers"]
        queries = []
        
        for cluster_id in range(len(centers)):
            # 클러스터에 속한 상품 인덱스 찾기
            cluster_item_indices = [i for i, label in enumerate(labels) if label == cluster_id]
            
            if not cluster_item_indices:
                continue
                
            # 중심점과 가장 가까운 상품 찾기
            similarities = [
                cosine_similarity([centers[cluster_id]], [embeddings[idx]])[0][0]
                for idx in cluster_item_indices
            ]
            
            closest_idx = cluster_item_indices[np.argmax(similarities)]
            closest_product = bookmarks[closest_idx]
            
            # 대표 키워드로 상품 제목 사용
            product_title = closest_product.get("title", "")
            if product_title:
                # 제목 전처리 (HTML 태그, 따옴표 제거)
                clean_title = clean_html(product_title)
                
                # 검색에 적합한 키워드 생성
                # 긴 제목의 경우 주요 키워드만 추출 (처음 3-4단어)
                keywords = ' '.join(clean_title.split()[:4])
                queries.append(keywords)
        
        return queries
    
    def get_recommendations(self, user_id: str, max_products: int = 20) -> List[Dict]:
        """사용자별 개인화된 추천 상품 가져오기"""
        # 북마크 가져오기
        bookmarks = self.get_user_bookmarks(user_id)
        
        if not bookmarks:
            # 북마크가 없는 경우 인기 상품 반환 (구현 필요)
            return []
        
        # 북마크 클러스터링하여 검색 쿼리 생성 및 중심점 가져오기
        search_queries, cluster_centers = self.cluster_bookmarks(bookmarks)
        
        # 하이브리드 추천 접근법:
        # 1. Pinecone 유사도 검색 기반 추천
        pinecone_recommendations = self._get_pinecone_recommendations(
            cluster_centers, bookmarks, max_products // 2)
            
        # 2. Naver Shopping API 기반 추천
        api_recommendations = self._get_api_recommendations(
            search_queries, bookmarks, max_products // 2)
        
        # 두 결과 결합
        combined_recommendations = pinecone_recommendations + api_recommendations
        
        # 중복 제거
        unique_recommendations = self._deduplicate_recommendations(combined_recommendations)
        
        # 최대 개수 제한
        return unique_recommendations[:max_products]
    
    def _get_pinecone_recommendations(self, cluster_centers: List[List[float]], 
                                    bookmarks: List[Dict], max_count: int) -> List[Dict]:
        """Pinecone 벡터 검색 기반 추천"""
        if not cluster_centers:
            return []
            
        # 이미 북마크한 상품 ID 목록
        bookmarked_ids = [bookmark.get("item_id") for bookmark in bookmarks]
        
        all_recommendations = []
        
        # 각 클러스터 중심점마다 유사 상품 검색
        for center in cluster_centers:
            similar_products = self.find_similar_products(
                embedding=center,
                top_k=max_count // len(cluster_centers) + 1,  # 클러스터 개수에 따라 분배
                exclude_ids=bookmarked_ids
            )
            all_recommendations.extend(similar_products)
        
        return all_recommendations
    
    def _get_api_recommendations(self, search_queries: List[str], 
                               bookmarks: List[Dict], max_count: int) -> List[Dict]:
        """네이버 쇼핑 API 기반 추천"""
        if not search_queries:
            return []
            
        # 이미 북마크한 상품 ID 목록
        bookmarked_ids = set(bookmark.get("item_id") for bookmark in bookmarks)
        
        all_products = []
        products_per_query = max(1, max_count // len(search_queries))
        
        # 각 쿼리로 검색 실행
        for query in search_queries:
            # 기존 search_naver_shopping 함수 사용
            products = search_naver_shopping(query)
            
            # 상품 형식 변환 및 북마크된 상품 제외
            formatted_products = []
            for product in products:
                if product.get("productId") not in bookmarked_ids:
                    formatted_product = {
                        "item_id": product.get("productId"),
                        "title": product.get("title", ""),
                        "price": product.get("price", product.get("lprice", "")),
                        "mall_name": product.get("mall_name", product.get("mallName", "")),
                        "product_url": product.get("link", ""),
                        "image_url": product.get("image", "")
                    }
                    formatted_products.append(formatted_product)
                    
                    # 검색된 상품도 Pinecone에 저장 (선택사항)
                    if len(formatted_products) <= 5:  # 상위 5개만 저장하여 DB 부하 감소
                        self.store_product_embeddings([formatted_product])
            
            all_products.extend(formatted_products[:products_per_query])
        
        return all_products
    
    def _deduplicate_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """추천 상품 중복 제거"""
        unique_products = []
        seen_ids = set()
        seen_titles = set()
        
        for product in recommendations:
            product_id = product.get("item_id", "")
            title = product.get("title", "")
            
            # ID와 제목 모두 중복 체크
            if product_id and product_id not in seen_ids and title not in seen_titles:
                seen_ids.add(product_id)
                seen_titles.add(title)
                unique_products.append(product)
        
        return unique_products

    @lru_cache(maxsize=100)
    def get_cached_recommendations(self, user_id: str, cache_time: str) -> List[Dict]:
        """캐싱된 추천 결과 가져오기"""
        return self.get_recommendations(user_id)