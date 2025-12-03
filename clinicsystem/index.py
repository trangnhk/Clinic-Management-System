import cloudinary.uploader
from flask import render_template, request, redirect
from flask_login import current_user, login_user, logout_user
from clinicsystem import app, dao, login, db
from datetime import datetime

# INDEX
@app.route("/")
def index():
    return render_template("index.html")

@app.context_processor
def commit_attribute():
    return {
        "menu_bar": dao.load_menu_bar()
    }

# LOGIN
@login.user_loader
def load_user(user_id):
    return dao.get_user_id(user_id)

@app.route("/login", methods=['get', 'post'])
def login_my_user():

    if current_user.is_authenticated:
        return redirect("/")

    if request.method.__eq__("POST"):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_account(username, password)

        if user:
            login_user(user)
            next = request.args.get('next')
            return redirect(next if next else '/')
            # return redirect("/")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=['GET', 'POST'])
def register_user():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not password.__eq__(confirm):
            err_msg = 'Mật khẩu không khớp!'
        else:
            data = request.form.copy()
            del data['confirm']
            avatar = request.files.get('avatar')
            file_path = None

            if avatar:
                res = cloudinary.uploader.upload(avatar)
                file_path = res['secure_url']

            try:
                dao.add_user(avatar=file_path, **data, dob=datetime(2005, 8, 30))
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


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
