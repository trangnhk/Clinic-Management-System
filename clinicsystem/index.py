import cloudinary.uploader
from flask import render_template, request, redirect
from flask_login import current_user, login_user, logout_user, login_required
from clinicsystem import app, dao, login, db
from datetime import datetime

from clinicsystem.decorators import anonymous_required
from clinicsystem.models import Nurse, Doctor, Cashier, Administrator, Patient


# INDEX
@app.route("/")
def index():
    return render_template("index.html")


@app.context_processor
def load_menu_bar():
    if current_user.is_authenticated:
        if isinstance(current_user, Nurse):
            return {"menu_bar": dao.load_menu_bar_nurse()}
        # elif isinstance(current_user, Doctor):
        #     return {"menu_bar": dao.load_menu_bar_doctor()}
        # elif isinstance(current_user, Cashier):
        #     return {"menu_bar": dao.load_menu_bar_cashier()}
        # elif isinstance(current_user, Administrator):
        #     return {"menu_bar": dao.load_menu_bar_admin()}

    # Default
    return {"menu_bar": dao.load_menu_bar()}

# LOGIN
@login.user_loader
def load_user(user_id):
    return (
        Patient.query.get(user_id)
        or Nurse.query.get(user_id)
        or Doctor.query.get(user_id)
        or Cashier.query.get(user_id)
        or Administrator.query.get(user_id)
    )

ROLE_REDIRECT = {
    "Nurse": "/nurse",
    "Doctor": "/doctor",
    "Cashier": "/cashier",
    "Administrator": "/admin"
}

@app.route("/login", methods=['get', 'post'])
@anonymous_required
def login_my_user():

    err_msg = None

    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_account(username, password)

        if user:
            login_user(user)
            next = request.args.get('next')
            return redirect(next if next else ROLE_REDIRECT.get(user.__class__.__name__, "/"))
            # return redirect("/")
        err_msg = "USERNAME HOẶC PASSWORD SAI!"
    return render_template("login.html", err_msg=err_msg)

# REGISTER
@app.route("/register", methods=['GET', 'POST'])
def register_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        username = request.form.get('username')
        phone = request.form.get('phone_number')

        # 1. CHECK PASSWORD
        if not password.__eq__(confirm):
            err_msg = 'Mật khẩu không khớp!'
        elif dao.get_user_by_username(username):
            err_msg = 'Username đã tồn tại!'
        elif dao.get_user_by_phone(phone):
            err_msg = 'SDT đã tồn tại!'
        else:
            data = {
                "username": request.form.get("username"),
                "password": request.form.get("password"),
                "fullname": request.form.get("fullname"),
                "phone_number": request.form.get("phone_number"),
                "gender": request.form.get("gender"),
                "dob": request.form.get("dob")
            }
            avatar = request.files.get('avatar')
            file_path = None

            if avatar:
                res = cloudinary.uploader.upload(avatar)
                file_path = res['secure_url']

            try:

                dao.add_user(avatar=file_path, **data)
                return redirect('/login')
            except:
                db.session.rollback()
                err_msg = "HỆ THỐNG ĐANG BỊ LỖI, VUI LÒNG QUAY LẠI"

    return render_template('register.html', err_msg=err_msg)

# LOGOUT
@app.route('/logout')
def logout_my_user():
    logout_user()
    return redirect('/login')

# NURSE
@app.route('/nurse')
@login_required
def nurse_home_info():
    return render_template('home_info.html', user=current_user, role="nurse")

# DOCTOR
@app.route('/doctor')
@login_required
def doctor_home_info():
    return render_template('home_info.html', user=current_user, role="doctor")

# CASHIER
@app.route('/cashier')
@login_required
def cashier_home_info():
    return render_template('home_info.html', user=current_user, role="cashier")

# ADMIN
@app.route('/admin')
@login_required
def admin_home_info():
    return render_template('home_info.html', user=current_user, role="admin")



if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
