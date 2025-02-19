# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin
# from werkzeug.security import generate_password_hash, check_password_hash

# db = SQLAlchemy()

# class User(UserMixin, db.Model):
#     __tablename__ = 'user'
    
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(100), unique=True, nullable=False, index=True)
#     password = db.Column(db.Text, nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False, index=True)
#     name = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20), nullable=False)

#     def set_password(self, password):
#         self.password = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password, password)

from flask_pymongo import PyMongo
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

mongo = PyMongo()

class User(UserMixin):
    def __init__(self, username, email, name, phone, password=None, _id=None):
        self.id = str(_id) if _id else None  # MongoDB의 _id는 ObjectId이므로 문자열 변환 필요
        self.username = username
        self.email = email
        self.name = name
        self.phone = phone
        if password:
            self.set_password(password)  # 비밀번호 해싱

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, self.password)

    def to_dict(self):
        """ MongoDB에 저장하기 위해 딕셔너리 형태로 변환 """
        return {
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "password": self.password  # 해싱된 비밀번호 저장
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
