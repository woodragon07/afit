# routes/recommendations.py
from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from services.recommendation import RecommendationService
import pymongo
from dotenv import load_dotenv
import os
from functions.utils import search_naver_shopping

load_dotenv()

api_key = os.getenv('API_KEY')
api_key = os.getenv('API_KEY')
api_key = os.getenv('API_KEY')
api_key = os.getenv('API_KEY')
print(api_key)  # API 키 출력

# Blueprint 생성
bp = Blueprint('recommendations', __name__)

# 추천 서비스 인스턴스
recommendation_service = RecommendationService()

# 방법 2: 서비스에서 db 연결 가져오기
from services.recommendation import db  # recommendation.py에서 db 가져오기

# @bp.route('/api/recommendations', methods=['GET'])
# def get_recommendations():
#     """사용자별 개인화된 추천 상품 API"""
#     user_id = request.args.get('userId')
    
#     if not user_id:
#         return jsonify({"success": False, "message": "사용자 ID가 필요합니다"}), 400
    
#     try:
#         # 캐싱을 위한 시간대 계산 (1시간 단위)
#         cache_time = datetime.now().strftime("%Y-%m-%d-%H")
        
#         # 캐싱된 추천 가져오기
#         recommendations = recommendation_service.get_cached_recommendations(user_id, cache_time)
        
#         if not recommendations:
#             return jsonify({
#                 "success": True, 
#                 "data": [], 
#                 "message": "추천 상품이 없습니다. 더 많은 상품을 북마크해 보세요."
#             })
        
#         return jsonify({"success": True, "data": recommendations})
#     except Exception as e:
#         current_app.logger.error(f"추천 생성 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": "추천을 처리하는 중 오류가 발생했습니다"}), 500

@bp.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID가 필요합니다"}), 400
    
    try:
        # 원래 추천 로직 시도
        recommendations = recommendation_service.get_recommendations(user_id)
        
        # 결과가 없으면 강제 추천 로직 사용
        if not recommendations or len(recommendations) == 0:
            print("기본 추천 결과 없음, 강제 추천 로직 사용")
            
            # 북마크 가져오기
            bookmarks = list(db.product_bookmark.find({"user_id": user_id}))
            
            if bookmarks:
                # 클러스터링 시도
                try:
                    queries, _ = recommendation_service.cluster_bookmarks(bookmarks)
                except:
                    queries = []
                
                # 쿼리가 없으면 샘플 쿼리 사용
                if not queries or len(queries) == 0:
                    titles = [b.get("title", "") for b in bookmarks]
                    sample_queries = ["노트북", "스마트폰", "이어폰", "의류"]
                    
                    for title in titles:
                        words = title.split()
                        if words and len(words) > 0:
                            sample_queries.append(words[0])
                    
                    queries = sample_queries[:3]
                
                # 네이버 쇼핑 API 검색
                def search_naver_shopping(query):
                    import requests
                    import urllib.parse
                    
                    try:
                        NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
                        NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")
                        
                        url = f"https://openapi.naver.com/v1/search/shop.json?query={urllib.parse.quote(query)}&display=10"
                        headers = {
                            "X-Naver-Client-Id": NAVER_CLIENT_ID,
                            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
                        }
                        resp = requests.get(url, headers=headers)
                        
                        if resp.status_code != 200:
                            return []
                        
                        items = resp.json().get("items", [])
                        return items
                    except:
                        return []
                
                # 검색 결과 수집
                all_products = []
                for query in queries[:3]:
                    products = search_naver_shopping(query)
                    all_products.extend(products[:5])
                
                # 중복 제거 및 형식 변환
                unique_products = []
                seen_ids = set()
                
                for product in all_products:
                    product_id = product.get("productId", "")
                    if product_id and product_id not in seen_ids:
                        seen_ids.add(product_id)
                        
                        formatted_product = {
                            "item_id": product.get("productId", ""),
                            "title": product.get("title", ""),
                            "price": product.get("lprice", ""),
                            "mall_name": product.get("mallName", ""),
                            "product_url": product.get("link", ""),
                            "image_url": product.get("image", "")
                        }
                        unique_products.append(formatted_product)
                
                recommendations = unique_products[:10]
        
        if not recommendations:
            return jsonify({
                "success": True, 
                "data": [], 
                "message": "추천 상품이 없습니다. 더 많은 상품을 북마크해 보세요."
            })
        
        return jsonify({"success": True, "data": recommendations})
    except Exception as e:
        print(f"추천 생성 중 오류: {str(e)}")
        return jsonify({"success": False, "message": "추천을 처리하는 중 오류가 발생했습니다"}), 500


@bp.route('/api/recommendations/refresh', methods=['POST'])
def refresh_recommendations():
    """추천 캐시 갱신 API"""
    user_id = request.json.get('userId')
    
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID가 필요합니다"}), 400
    
    try:
        # 강제로 캐시를 무시하고 새로운 추천 생성
        recommendations = recommendation_service.get_recommendations(user_id)
        
        return jsonify({
            "success": True, 
            "data": recommendations,
            "message": "추천이 갱신되었습니다."
        })
    except Exception as e:
        current_app.logger.error(f"추천 갱신 중 오류: {str(e)}")
        return jsonify({"success": False, "message": "추천을 갱신하는 중 오류가 발생했습니다"}), 500

@bp.route('/api/recommendations/store', methods=['POST'])
def store_product_embeddings():
    """상품 임베딩 저장 API (관리자용)"""
    products = request.json.get('products', [])
    
    if not products:
        return jsonify({"success": False, "message": "저장할 상품 데이터가 필요합니다"}), 400
    
    try:
        success = recommendation_service.store_product_embeddings(products)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"{len(products)}개 상품의 임베딩이 저장되었습니다."
            })
        else:
            return jsonify({
                "success": False,
                "message": "임베딩 저장 중 오류가 발생했습니다."
            }), 500
    except Exception as e:
        current_app.logger.error(f"임베딩 저장 중 오류: {str(e)}")
        return jsonify({"success": False, "message": "임베딩을 저장하는 중 오류가 발생했습니다"}), 500
    
#----------------------------------------------
#강제 API 호출 테스트
@bp.route('/api/recommendations/force-test', methods=['GET'])
def force_recommendations():
    """강제 추천 생성 테스트 API"""
    user_id = request.args.get('userId')
    
    if not user_id:
        return jsonify({"success": False, "message": "사용자 ID가 필요합니다"})
    
    try:
        # 북마크 가져오기
        bookmarks = list(db.product_bookmark.find({"user_id": user_id}))
        
        if not bookmarks:
            return jsonify({"success": False, "message": "북마크가 없습니다"})
        
        # 클러스터링 및 쿼리 생성
        queries, centers = recommendation_service.cluster_bookmarks(bookmarks)
        
        # 클러스터링 결과가 없는 경우 대체 쿼리 사용
        if not queries or len(queries) == 0:
            sample_queries = ["노트북", "스마트폰", "이어폰", "의류"]
            
            # 북마크 제목에서 키워드 추출
            titles = [b.get("title", "") for b in bookmarks]
            for title in titles:
                words = title.split()
                if words and len(words) > 0:
                    sample_queries.append(words[0])  # 첫 단어만 사용
            
            queries = sample_queries[:3]  # 최대 3개 쿼리 사용
        
        # 네이버 쇼핑 API 검색 함수 찾기
        search_func = None
        
        # 방법 1: 직접 함수 정의 (추천 서비스에서 사용하는 방식과 동일)
        def search_naver_shopping(query, price_range=None):
            import requests
            import urllib.parse
            
            try:
                sort_option = "sim"
                if price_range and price_range.get("sort") == "price_asc":
                    sort_option = "asc"
                    
                # API 키는 환경변수나 설정에서 가져오기
                NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
                NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")
                
                url = f"https://openapi.naver.com/v1/search/shop.json?query={urllib.parse.quote(query)}&display=20&sort={sort_option}"
                headers = {
                    "X-Naver-Client-Id": NAVER_CLIENT_ID,
                    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
                }
                resp = requests.get(url, headers=headers)
                
                if resp.status_code != 200:
                    return []
                    
                items = resp.json().get("items", [])
                return items
            except Exception as e:
                print(f"네이버 쇼핑 API 호출 중 오류: {str(e)}")
                return []
        
        search_func = search_naver_shopping
        
        # 검색 함수를 사용하여 상품 가져오기
        all_products = []
        for query in queries[:3]:  # 최대 3개 쿼리만 사용
            try:
                products = search_func(query)
                all_products.extend(products[:5])  # 각 쿼리당 최대 5개 상품
            except Exception as e:
                print(f"쿼리 '{query}' 검색 중 오류: {str(e)}")
        
        # 중복 제거
        unique_products = []
        seen_ids = set()
        
        for product in all_products:
            product_id = product.get("productId", "")
            if product_id and product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_products.append(product)
        
        # 상품 정보 형식 변환 (필요한 경우)
        formatted_products = []
        for product in unique_products:
            formatted_product = {
                "item_id": product.get("productId", ""),
                "title": product.get("title", ""),
                "price": product.get("lprice", ""),
                "mall_name": product.get("mallName", ""),
                "product_url": product.get("link", ""),
                "image_url": product.get("image", "")
            }
            formatted_products.append(formatted_product)
        
        return jsonify({
            "success": True,
            "data": formatted_products[:10],  # 최대 10개만 반환
            "message": "강제 추천 생성 완료"
        })
    except Exception as e:
        print(f"강제 추천 생성 중 오류: {str(e)}")
        return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})
    

# #프론트 테스트
# @bp.route('/api/recommendations/force', methods=['GET'])
# def force_recommendations():
#     """강제 추천 생성 테스트 API"""
#     user_id = request.args.get('userId')
    
#     if not user_id:
#         return jsonify({"success": False, "message": "사용자 ID가 필요합니다"})
    
#     try:
#         # 북마크 가져오기
#         bookmarks = list(db.product_bookmark.find({"user_id": user_id}))
        
#         if not bookmarks:
#             return jsonify({"success": False, "message": "북마크가 없습니다"})
        
#         # 클러스터링 및 쿼리 생성
#         queries, centers = recommendation_service.cluster_bookmarks(bookmarks)
        
#         # 클러스터링 결과가 없는 경우 대체 쿼리 사용
#         if not queries or len(queries) == 0:
#             sample_queries = ["노트북", "스마트폰", "이어폰", "의류"]
            
#             # 북마크 제목에서 키워드 추출
#             titles = [b.get("title", "") for b in bookmarks]
#             for title in titles:
#                 words = title.split()
#                 if words and len(words) > 0:
#                     sample_queries.append(words[0])  # 첫 단어만 사용
            
#             queries = sample_queries[:3]  # 최대 3개 쿼리 사용
        
#         # 네이버 쇼핑 API 검색
#         from function.utils import search_naver_shopping
        
#         all_products = []
#         for query in queries[:3]:  # 최대 3개 쿼리만 사용
#             try:
#                 products = search_naver_shopping(query)
#                 all_products.extend(products[:5])  # 각 쿼리당 최대 5개 상품
#             except Exception as e:
#                 print(f"쿼리 '{query}' 검색 중 오류: {str(e)}")
        
#         # 중복 제거
#         unique_products = []
#         seen_ids = set()
        
#         for product in all_products:
#             product_id = product.get("productId", "")
#             if product_id and product_id not in seen_ids:
#                 seen_ids.add(product_id)
#                 unique_products.append(product)
        
#         # 상품 정보 형식 변환 (필요한 경우)
#         formatted_products = []
#         for product in unique_products:
#             formatted_product = {
#                 "item_id": product.get("productId", ""),
#                 "title": product.get("title", ""),
#                 "price": product.get("lprice", ""),
#                 "mall_name": product.get("mallName", ""),
#                 "product_url": product.get("link", ""),
#                 "image_url": product.get("image", "")
#             }
#             formatted_products.append(formatted_product)
        
#         return jsonify({
#             "success": True,
#             "data": formatted_products[:10],  # 최대 10개만 반환
#             "message": "강제 추천 생성 완료"
#         })
#     except Exception as e:
#         print(f"강제 추천 생성 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})
    


# #API 테스트
# @bp.route('/api/recommendations/debug', methods=['GET'])
# def debug_recommendations():
#     """추천 시스템 디버깅 API"""
#     user_id = request.args.get('userId')
    
#     if not user_id:
#         return jsonify({"success": False, "message": "사용자 ID가 필요합니다"})
    
#     try:
#         # 1. 사용자 북마크 가져오기
#         bookmarks = list(db.product_bookmark.find({"user_id": user_id}))
        
#         # 북마크가 없는 경우
#         if not bookmarks:
#             return jsonify({"success": False, "message": "북마크가 없습니다"})
        
#         # 2. 북마크 제목 추출
#         titles = [bookmark.get("title", "") for bookmark in bookmarks]
        
#         # 3. 클러스터링 시도
#         embeddings = recommendation_service.generate_embeddings(titles)
        
#         # 4. 쿼리 생성
#         queries, centers = recommendation_service.cluster_bookmarks(bookmarks)
        
#         # 5. 테스트 검색
#         search_results = []
#         for query in queries:
#             # 올바른 위치에서 함수 가져오기
#             try:
#                 from function.utils import search_naver_shopping
#                 results = search_naver_shopping(query)
#                 search_results.append({
#                     "query": query,
#                     "results_count": len(results),
#                     "samples": results[:2]  # 첫 2개만 표시
#                 })
#             except Exception as e:
#                 search_results.append({
#                     "query": query,
#                     "error": f"검색 오류: {str(e)}"
#                 })
        
#         # 6. Pinecone 유사도 검색 시도
#         pinecone_results = []
#         try:
#             if hasattr(recommendation_service, '_get_pinecone_recommendations'):
#                 # 첫 번째 센터만 테스트
#                 if centers and len(centers) > 0:
#                     similar_products = recommendation_service._get_pinecone_recommendations(
#                         [centers[0]], bookmarks, 5)
#                     pinecone_results = similar_products
#         except Exception as e:
#             pinecone_results = f"Pinecone 검색 오류: {str(e)}"
        
#         return jsonify({
#             "success": True,
#             "bookmarks_count": len(bookmarks),
#             "bookmark_titles": titles[:5],  # 처음 5개만 표시
#             "embeddings_count": len(embeddings),
#             "embedding_dimension": len(embeddings[0]) if embeddings else 0,
#             "queries_generated": queries,
#             "search_results": search_results,
#             "pinecone_results": pinecone_results
#         })
#     except Exception as e:
#         print(f"추천 디버깅 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})


# #Pinecone 테스트
# @bp.route('/api/recommendations/test-pinecone-detailed', methods=['GET'])
# def test_pinecone_detailed():
#     """Pinecone 연결 상세 테스트 API"""
#     try:
#         # 1. Pinecone 설정 확인
#         pinecone_settings = {
#             'api_key': recommendation_service.pinecone_api_key,
#             'environment': recommendation_service.pinecone_environment,
#             'index_name': recommendation_service.pinecone_index_name
#         }
        
#         # 2. Pinecone 클라이언트 확인
#         pinecone_client_type = str(type(recommendation_service.pc))
        
#         # 3. 인덱스 객체 확인
#         index_type = str(type(recommendation_service.index))
        
#         # 4. 인덱스 초기화 메서드 확인
#         if hasattr(recommendation_service, '_initialize_pinecone'):
#             try:
#                 recommendation_service._initialize_pinecone()
#                 init_result = "Pinecone 인덱스 초기화 성공"
#             except Exception as e:
#                 init_result = f"Pinecone 인덱스 초기화 실패: {str(e)}"
#         else:
#             init_result = "초기화 메서드 없음"
        
#         return jsonify({
#             "success": True,
#             "pinecone_settings": pinecone_settings,
#             "pinecone_client_type": pinecone_client_type,
#             "index_type": index_type,
#             "initialization_result": init_result
#         })
#     except Exception as e:
#         print(f"Pinecone 상세 테스트 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})


# #테스트
# @bp.route('/api/recommendations/test-bookmarks', methods=['GET'])
# def test_bookmarks():
#     """북마크 데이터 확인 API"""
#     try:
#         # 모든 북마크 카운트
#         count = db.product_bookmark.count_documents({})
        
#         # 샘플 데이터 가져오기 (최대 3개)
#         samples = list(db.product_bookmark.find().limit(3))
        
#         # 개인정보 제거
#         for sample in samples:
#             if '_id' in sample:
#                 sample['_id'] = str(sample['_id'])
        
#         return jsonify({
#             "success": True,
#             "total_bookmarks": count,
#             "samples": samples
#         })
#     except Exception as e:
#         print(f"북마크 테스트 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})

# @bp.route('/api/recommendations/test-pinecone', methods=['GET'])
# def test_pinecone():
#     """Pinecone 연결 테스트 API"""
#     try:
#         # Pinecone 인덱스 정보 가져오기
#         index_stats = recommendation_service.index.describe_index_stats()
        
#         return jsonify({
#             "success": True,
#             "message": "Pinecone 연결 성공",
#             "index_stats": index_stats
#         })
#     except Exception as e:
#         print(f"Pinecone 연결 테스트 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})

# @bp.route('/api/recommendations/test-embedding', methods=['GET'])
# def test_embedding():
#     """임베딩 저장 테스트 API"""
#     try:
#         # MongoDB에서 북마크 데이터 가져오기 (최대 5개)
#         bookmarks = list(db.product_bookmark.find().limit(5))
        
#         if not bookmarks:
#             return jsonify({"success": False, "message": "북마크 데이터가 없습니다"})
        
#         # 임베딩 생성 및 저장 테스트
#         success = recommendation_service.store_product_embeddings(bookmarks)
        
#         return jsonify({
#             "success": success,
#             "message": "임베딩 테스트 완료",
#             "tested_items": len(bookmarks)
#         })
#     except Exception as e:
#         print(f"임베딩 테스트 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})

# @bp.route('/api/recommendations/test-all', methods=['GET'])
# def test_all():
#     """전체 추천 시스템 테스트 API"""
#     results = {}
    
#     try:
#         # 1. 북마크 데이터 확인
#         bookmark_count = db.product_bookmark.count_documents({})
#         results['bookmarks'] = {
#             'success': True,
#             'count': bookmark_count,
#             'message': f'{bookmark_count}개의 북마크 데이터 확인됨'
#         }
        
#         # 2. Pinecone 연결 확인
#         try:
#             index_stats = recommendation_service.index.describe_index_stats()
#             results['pinecone'] = {
#                 'success': True,
#                 'message': 'Pinecone 연결 성공',
#                 'vector_count': index_stats.get('totalVectorCount', 0)
#             }
#         except Exception as e:
#             results['pinecone'] = {
#                 'success': False,
#                 'message': f'Pinecone 연결 오류: {str(e)}'
#             }
        
#         # 3. 샘플 임베딩 생성 테스트
#         try:
#             sample_text = ['테스트 임베딩 생성']
#             embeddings = recommendation_service.generate_embeddings(sample_text)
#             results['embedding'] = {
#                 'success': len(embeddings) > 0,
#                 'message': '임베딩 생성 성공',
#                 'dimension': len(embeddings[0]) if embeddings else 0
#             }
#         except Exception as e:
#             results['embedding'] = {
#                 'success': False,
#                 'message': f'임베딩 생성 오류: {str(e)}'
#             }
        
#         return jsonify({
#             "success": True,
#             "results": results
#         })
#     except Exception as e:
#         print(f"테스트 중 오류: {str(e)}")
#         return jsonify({"success": False, "message": f"오류 발생: {str(e)}"})