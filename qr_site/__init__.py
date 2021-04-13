from datetime import datetime

from flask import Flask
from os import path
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Константы для загрузки файла
# Сохраняет в корень локальной машины


UPLOAD_FOLDER = '/Project_QR/Site/sweater/static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# path.abspath()
# print(CONSTANT_BASE_PATH)
# SQLALCHEMY_DATABASE_URI = 'mysql://user:testqr12345678@80.78.245.132/main_db'

# login_manager = LoginManager()

app = Flask(__name__)

app.config['FLASK_ENV'] = 'development'
# Путь Папки сохранения
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.permanent_session_lifetime = datetime.timedelta(days=365)
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI


# db = SQLAlchemy(app)
#
# login_manager.init_app(app)
# login_manager.login_view = 'login_page'

from qr_site import models, routes
