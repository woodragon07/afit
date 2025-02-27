# routes/recommendation_page_routes.py

from flask import Blueprint, render_template, session

# Blueprint 생성
bp = Blueprint('recommendation_page', __name__)

@bp.route('/recommendations')
def recommendations_page():
    """추천 상품 페이지 렌더링"""
    # KO 폴더 내의 템플릿 경로로 수정
    user_id = session.get('user_id', '')
    return render_template('KO/recommendations.html', user_id=user_id)