import cloudinary.uploader
from flask import json

from clinicsystem.models import User, Patient, Nurse, Doctor, Cashier, UserGender
from clinicsystem import app, db
import hashlib


# USER
def auth_account(username, password, role=None):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()

    u = User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password))

    if role:
        u = u.filter(User.role.__eq__(role))

    return u.first()


def get_user_id(user_id):
    return db.session.get(User, user_id)

def add_user(fullname, username, password, phone_number, dob=None, gender=None, avatar = None):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    u = User(fullname=fullname, username=username, password=password, phone_number=phone_number, dob=dob, gender=UserGender.MALE,
             avatar=avatar)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        u.avatar = res.get("secure_url")



    db.session.add(u)
    db.session.commit()

# DEFAULT
def load_menu_bar():
    with open("data/menu_bar.json", encoding="utf-8") as f:
        return json.load(f)


