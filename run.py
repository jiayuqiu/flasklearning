#!flask/bin/python
from flask import Flask, g, jsonify
from flask_httpauth import HTTPTokenAuth
from flask import Blueprint
# from flask_zookeeper import FlaskZookeeperClient
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

import logging
from logging.handlers import TimedRotatingFileHandler

from weather.clf import weather_clf

user = 'root'
passwd = 'Root@123'
host = '192.168.7.209'
port = 13306
database = 'tab_user_info'

app = Flask(__name__,)
app.register_blueprint(weather_clf, url_prefix='/weather_clf/')  # add weather clf

# add token conf
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{passwd}@{host}:{port}/{database}?charset=utf8"
app.config['SECRET_KEY'] = 'top secret!'
# app.config.from_object(BaseConfig)


# set token
token_serializer = Serializer(app.config['SECRET_KEY'], expires_in=3600)

auth = HTTPTokenAuth('Bearer')

users = ['john', 'susan']
for user in users:
    token = token_serializer.dumps({'username': user}).decode('utf-8')
    print('*** token for {}: {}\n'.format(user, token))


@auth.verify_token
def verify_token(token):
    try:
        data = token_serializer.loads(token)
    except:
        return 'token 过期'
    if 'username' in data:
        return data['username']


@app.route('/')
@auth.login_required
def index():
    app.logger.info("Info message")
    app.logger.warning("Warning msg")
    app.logger.error("Error msg----1")
    app.logger.error("Error msg----2")
    app.logger.error("Error msg----3")
    app.logger.info(f"Info message: {auth.current_user()} log in.")
    return "Hello, %s!" % auth.current_user()


if __name__ == "__main__":
    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler(
        "flask.log", when="D", interval=1, backupCount=15,
        encoding="UTF-8", delay=False, utc=True)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=18888, debug=True)
