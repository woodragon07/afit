> 이 프로젝트는 Python 기반의 웹 애플리케이션입니다.  
> 가상환경을 설정하고 필요한 패키지를 설치한 후 실행하는 방법을 설명합니다.

##  **프로젝트 실행 방법**
이 프로젝트를 실행하려면 **Python 3.x 버전과 Conda**가 필요합니다.  
아래 단계를 차례로 따라가세요.

1️⃣ 가상환경 생성 
먼저, Conda를 이용해 새로운 가상환경을 생성합니다.

conda create -n 환경이름 python=3.X (버전)

2️⃣ 가상환경 활성화
conda activate 환경이름

3️⃣ 필수 패키지 설치
pip install -r requirement_pip_list.txt

4️⃣ 프로젝트 폴더로 이동
cd dfit

5️⃣ 애플리케이션 실행
python app.py

## 📁 프로젝트 폴더 구조
이 프로젝트는 다음과 같은 폴더 구조를 가집니다.
├── DFIT_FRONT
│   ├── dfit
│   │   ├── __pycache__
│   │   ├── functions
│   │   │   ├── __pycache__
│   │   │   ├── __init__.py
│   │   │   ├── en_secretary.py
│   │   │   ├── secretary.py
│   │   │   └── utils.py
│   │   ├── instance
│   │   │   └── users.db
│   │   ├── routes
│   │   │   ├── __pycache__
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py
│   │   │   ├── bookmark_routes.py
│   │   │   ├── chatrecommendation_routes.py
│   │   │   ├── en_chatrecommendation_routes.py
│   │   │   ├── en_shopping_secretary_routes.py
│   │   │   ├── product_routes.py
│   │   │   ├── recommendation_page_routes.py
│   │   │   ├── recommendations.py
│   │   │   ├── shopping_secretary.py
│   │   │   ├── trans.py
│   │   │   └── vsssssa12-10.py
│   │   ├── services
│   │   │   ├── __pycache__
│   │   │   ├── __init__.py
│   │   │   ├── db.py
│   │   │   └── recommendation.py
│   │   ├── shopping_file
│   │   │   ├── __pycache__
│   │   │   ├── __init__.py
│   │   │   ├── en_generate_platform_basket_html.py
│   │   │   ├── generate_platform_basket_html.py
│   │   │   ├── parse_shopping_result.py
│   │   │   └── search_platform_items.py
│   │   └── static
│   │       ├── iconimages
│   │       │   ├── bookmark.png
│   │       │   ├── home.png
│   │       │   ├── language.png
│   │       │   ├── magnifier.png
│   │       │   └── recommended.png
│   │       ├── images
│   │       │   ├── 11st_logo.png
│   │       │   ├── coupang_logo.png
│   │       │   └── gmarket_log.png
│   │       ├── js
│   │       │   ├── bookmark.js
│   │       │   ├── landing.js
│   │       │   ├── login.js
│   │       │   ├── recommendations.js
│   │       │   ├── search_EN.js
│   │       │   └── search.js
│   │       ├── styles
│   │       │   ├── bookmarks.css
│   │       │   ├── landingstyles.css
│   │       │   ├── login.css
│   │       │   ├── recommendations.css
│   │       │   ├── searchstyles.css
│   │       │   └── signup.css
│   │       ├── google_icon.png
│   │       ├── kakao_icon.png
│   │       └── naver_icon.png
│   │   ├── templates
│   │       ├── EN
│   │       │   ├── landing_EN.html
│   │       │   ├── login_EN.html
│   │       │   ├── search_EN.html
│   │       │   └── signup_EN.html
│   │       ├── KO
│   │       │   ├── bookmarks.html
│   │       │   ├── landing.html
│   │       │   ├── login.html
│   │       │   ├── recommendations.html
│   │       │   ├── search.html
│   │       │   ├── signup.html
│   │       │   └── find_id.html
│   └── 개요팀
├── .env
├── .gitignore
├── afit.zip
├── apikey
├── app.py
├── conda_requirements.txt
├── config.py
├── database.py
├── extensions.py
├── README.md
├── requirement_pip_list.txt
├── requirements.txt
└── tw.txt