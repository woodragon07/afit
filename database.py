from flask_pymongo import PyMongo
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

mongo = PyMongo()

class User(UserMixin):
    def __init__(self, username, email, name, phone, password=None, _id=None):
        self.id = str(_id) if _id else None  # MongoDB의 _id는 ObjectId이므로 문자열 변환 필요ㅋ
        self.username = username
        self.email = email
        self.name = name
        self.phone = phone
        self.password = password

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        """ MongoDB에 저장하기 위해 딕셔너리 형태로 변환 """
        return {
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "password": self.password  # 해싱된 비밀번호 저장
            #ㅅㅂ존나힘드네
        }

    @staticmethod
    def from_dict(user_dict):
        """ MongoDB에서 불러온 데이터를 User 객체로 변환 """
        return User(
            username=user_dict["username"],
            email=user_dict["email"],
            name=user_dict["name"],
            phone=user_dict["phone"],
            password=user_dict["password"],
            _id=user_dict["_id"]
        )


# 북마크를 위한 새로운 클래스 추가
class Bookmark:
    def __init__(self, user_id, item_id, title, price, mall_name, product_url, image_url):
        self.user_id = user_id
        self.item_id = item_id
        self.title = title
        self.price = price
        self.mall_name = mall_name
        self.product_url = product_url
        self.image_url = image_url
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "item_id": self.item_id,
            "title": self.title,
            "price": self.price,
            "mall_name": self.mall_name,
            "product_url": self.product_url,
            "image_url": self.image_url,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        return Bookmark(
            user_id=data["user_id"],
            item_id=data["item_id"],
            title=data["title"],
            price=data["price"],
            mall_name=data["mall_name"],
            product_url=data["product_url"],
            image_url=data["image_url"]
        )