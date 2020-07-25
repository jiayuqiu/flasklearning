from flask import Flask
from .clf import weather_clf

app = Flask(__name__)

# 在api.gnizama.com中添加API蓝图
app.register_blueprint(weather_clf, subdomain='weather')
