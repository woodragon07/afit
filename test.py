import re
import urllib.parse
import requests
import json
from datetime import timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from utils import search_naver_shopping, format_price 
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from database import db, User
import os
from dotenv import load_dotenv

# ====== API Key 설정 ==========
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

print("Google API Key:", GOOGLE_API_KEY)
print("Naver Client ID:", NAVER_CLIENT_ID)
print("Naver Client Secret:", NAVER_CLIENT_SECRET)

genai.configure(api_key=GOOGLE_API_KEY)
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SESSION_PERMANENT'] = True  # False에서 True로 변경
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # 30일로 설정

# MySQL 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dldndyd@localhost/client_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB 초기화
db.init_app(app)

# 앱 시작시 테이블 생성
with app.app_context():
    try:
        # 테이블 생성
        db.create_all()
        print("데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"데이터베이스 테이블 생성 중 오류 발생: {str(e)}")

#######################
# (1) 랜딩 페이지
#######################
@app.route("/")
def landing():
    # 로그인 상태 확인
    user = session.get('user')
    return render_template("KO/landing.html", user=user)

@app.route("/english")
def english():
    # 로그인 상태 확인
    user = session.get('user')
    return render_template("EN/landing_EN.html", user=user)

@app.route("/search")
def search_page():
    # 로그인 상태 확인
    user = session.get('user')
    # 두 번째 화면(왼쪽 챗 + 오른쪽 상품)
    return render_template("KO/search.html", user=user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template("KO/login.html", username_error="존재하지 않는 아이디입니다.")
        
        if not user.check_password(password):
            return render_template("KO/login.html", password_error="비밀번호가 올바르지 않습니다.")
        
        session.permanent = True
        session['user'] = {
            'id': user.id,
            'name': user.name,
            'username': user.username
        }
        return redirect(url_for('landing'))

    return render_template("KO/login.html")

@app.route("/login_EN", methods=['GET', 'POST'])
def login_EN():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session.permanent = True  # 세션을 영구적으로 설정
            session['user'] = {
                'id': user.id,
                'name': user.name,
                'username': user.username
            }
            return redirect(url_for('english'))
        else:
            return "Login failed", 401

    return render_template("EN/login_EN.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')  # 비밀번호 확인 필드 추가
            email = request.form.get('email')
            name = request.form.get('name')
            phone = request.form.get('phone')
            
            print(f"회원가입 시도: username={username}, email={email}")
            
            # 비밀번호 확인 체크
            if password != password_confirm:
                return render_template("KO/signup.html", 
                    password_confirm_error="비밀번호가 일치하지 않습니다.",
                    username=username,  # 기존 입력값 유지
                    email=email,
                    name=name,
                    phone=phone
                )
            
            # 아이디 중복 체크
            if User.query.filter_by(username=username).first():
                print(f"아이디 중복: {username}")
                return render_template("KO/signup.html", 
                    username_error="이미 존재하는 아이디입니다.",
                    email=email,  # 기존 입력값 유지
                    name=name,
                    phone=phone
                )
                
            # 이메일 중복 체크    
            if User.query.filter_by(email=email).first():
                print(f"이메일 중복: {email}")
                return render_template("KO/signup.html", 
                    email_error="이미 존재하는 이메일입니다.",
                    username=username,  # 기존 입력값 유지
                    name=name,
                    phone=phone
                )
            
            if all([username, password, email, name, phone]):
                # 새 사용자 객체 생성
                new_user = User()
                new_user.username = username
                new_user.email = email
                new_user.name = name
                new_user.phone = phone
                new_user.set_password(password)
                
                # 데이터베이스에 추가
                db.session.add(new_user)
                db.session.commit()
                
                print(f"회원가입 성공: {username}")
                return redirect(url_for('login'))
            else:
                print("필수 필드 누락")
                return render_template("KO/signup.html", error="모든 필드를 입력해주세요")
                
        except Exception as e:
            db.session.rollback()
            print(f"회원가입 실패 상세: {str(e)}")
            return render_template("KO/signup.html", error=f"회원가입 실패: {str(e)}")

    return render_template("KO/signup.html")

@app.route("/signup_EN", methods=['GET', 'POST'])
def signup_EN():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        # Check for duplicate username
        if User.query.filter_by(username=username).first():
            return "Username already exists.", 400
            
        # Check for duplicate email
        if User.query.filter_by(email=email).first():
            return "Email already exists.", 400
        
        if username and password and email and name and phone:
            new_user = User(
                username=username,
                email=email,
                name=name,
                phone=phone
            )
            new_user.set_password(password)
            
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login_EN'))
            except Exception as e:
                db.session.rollback()
                return "Registration failed: " + str(e), 400
        else:
            return "Please fill in all fields", 400

    return render_template("EN/signup_EN.html")

@app.route('/logout')
def logout():
    # 세션에서 사용자 정보 제거
    session.pop('user', None)
    return redirect(url_for('landing'))

@app.route('/logout_EN') #영어 버젼젼
def logout_EN():
    # 세션에서 사용자 정보 제거
    session.pop('user', None)
    return redirect(url_for('landing_EN'))

def extract_price_range(text):
    """사용자 메시지에서 가격대, 최저가 등 간단 추출"""
    try:
        match = re.search(r'(\d+)만원대', text)
        if match:
            base = int(match.group(1))
            return {"min":base*10000, "max":(base+10)*10000 -1, "display":f"{base}만원대"}
        return None
    except:
        return None

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    mode = data.get("mode", "helper")  # 기본값은 helper
    
    if not user_message:
        return jsonify([{"response": "메시지를 입력하세요."}])
    
    if mode == "helper":
        price_range = extract_price_range(user_message)
        keywords = [user_message]
        found_items = []
        responses = []
        
        for kw in keywords:
            items = search_naver_shopping(kw, price_range)
            if items:
                found_items.extend(items)
                for it in items:
                    product_html = f"""
                    <div class="product-card">
                        <button class="bookmark-btn">
                            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </button>
                        <div class="product-image-container">
                            <img src="{it['image']}" alt="{it['title']}" class="product-image"/>
                        </div>
                        <div class="product-info">
                            <div class="product-meta">{it.get('mall_name','판매처 정보 없음')}</div>
                            <h3 class="product-title">{it['title']}</h3>
                            <div class="product-price">{it['formatted_price']}</div>
                            <div class="product-recommendation">추천 상품</div>
                            <div class="mt-4">
                                <a href="{it['link']}" target="_blank"
                                   class="block w-full text-center bg-[#FF9999] hover:bg-[#FF6B6B] text-white py-2 px-4 rounded-md transition-colors">
                                   제품 보기
                                </a>
                            </div>
                        </div>
                    </div>
                    """
                    responses.append({"response": product_html, "html": True})
        
        if found_items:
            minp = min(x["price"] for x in found_items)
            maxp = max(x["price"] for x in found_items)
            summary = f"💡 {format_price(minp)}~{format_price(maxp)} 범위의 상품을 찾았어요."
            responses.insert(0, {"response": summary})
        else:
            responses.append({"response": "😅 조건에 맞는 상품을 찾지 못했어요."})
        
        return jsonify(responses)
        
    elif mode == "shopping":
        # 쇼핑비서 모드는 secretary.py에서 처리
        from secretary import handle_shopping_secretary_mode
        responses = handle_shopping_secretary_mode(user_message, search_naver_shopping, format_price)
        return jsonify(responses)
    else:
        return jsonify([{"response": "지원하지 않는 모드입니다."}])

if __name__ == "__main__":
    app.run(debug=True, port=5000)