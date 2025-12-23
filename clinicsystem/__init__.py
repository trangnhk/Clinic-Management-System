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


from clinicsystem.nurse.routes import nurse_page
from clinicsystem.admin.routes import admin_page
from clinicsystem.cashier.routes import cashier_page
from clinicsystem.doctor import doctor_page
app.register_blueprint(nurse_page)
app.register_blueprint(admin_page)
app.register_blueprint(cashier_page)
app.register_blueprint(doctor_page)