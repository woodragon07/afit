# routes/product_routes.py 랜딩 페이지와 검색 페이지 관련 라우트를 담당
from flask import Blueprint, render_template, session

bp = Blueprint('product', __name__)

@bp.route("/")
def landing():
    user = session.get('user')
    return render_template("KO/landing.html", user=user)

@bp.route("/english")
def english():
    user = session.get('user')
    return render_template("EN/landing_EN.html", user=user)

@bp.route("/search")
def search_page():
    user = session.get('user')
    return render_template("KO/search.html", user=user)
