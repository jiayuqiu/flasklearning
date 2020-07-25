from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

user = 'root'
passwd = 'Root@123'
host = '192.168.7.209'
port = 13306
database = 'alg_user_db'
charset = 'utf8'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}?charset={charset}'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'tab_user_info'
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(32), index = True)
    password = db.Column(db.String(128))
    update_time = db.Column('update_time', db.DateTime(timezone=True), server_default=func.now())
    create_time = db.Column('create_time', db.DateTime(timezone=True), server_default=func.now())

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user