from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import configparser
import datetime
from databes import db
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# 設定資料庫連線地址
db_config = configparser.ConfigParser()
db_config.read('db_connect.ini')
def get_db_uri(cfg):
    res = "mysql+pymysql://" + cfg.get("user") + ":" + cfg.get("password") + "@" + cfg.get("host") + ":" + cfg.get("port") + "/" + cfg.get("database")    
    return res
conn = get_db_uri(db_config['DB_CONNECT'])
app.config['SQLALCHEMY_DATABASE_URI'] = conn
# 是否追蹤資料庫修改，一般不開啟，會影響效能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 是否顯示底層執行的 SQL 語句
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = '111DBMSfinal'

class User(db.Model, UserMixin):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(500), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    registration_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    is_active = db.Column(db.Boolean, server_default='1', nullable=False)
    
    def get_id(self):
        return str(self.user_id)    

class Poll(db.Model):
    __tablename__ = 'Poll'
    poll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_approved = db.Column(db.Boolean, server_default='0', nullable=False)

class Comment(db.Model):
    __tablename__ = 'Comment'
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('Poll.poll_id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('Comment.comment_id'), server_default=comment_id, nullable=True)
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[comment_id]), lazy='dynamic')

class Question(db.Model):
    __tablename__ = 'Question'
    poll_id = db.Column(db.Integer, db.ForeignKey('Poll.poll_id'), primary_key=True)
    question_id = db.Column(db.Integer, primary_key=True, index=True)
    text = db.Column(db.String(500), nullable=False)
    count_support = db.Column(db.Integer, server_default='0', nullable=True)
    count_oppose = db.Column(db.Integer, server_default='0', nullable=True)

class Vote(db.Model):
    __tablename__ = 'Vote'
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'), primary_key=True, nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('Question.poll_id'), primary_key=True, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('Question.question_id'), primary_key=True, nullable=False)
    option = db.Column(db.Boolean, nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

