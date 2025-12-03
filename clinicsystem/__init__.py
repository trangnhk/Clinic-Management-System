import cloudinary
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = "NGOHOANGKIEUTRANG"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Nhinho3008@localhost/clinicdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

cloudinary.config(cloud_name='dxfbpkmen',
                  api_key='771652583444831',
                  api_secret='EwZYOpA4n19unyDcRFEDBud6LBA')

login = LoginManager(app)
db = SQLAlchemy(app)