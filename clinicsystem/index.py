from flask import render_template, request, redirect
from flask_login import current_user, login_user, logout_user
from clinicsystem import app, dao, login

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
    return dao.get_user_by_id(user_id)

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
            return redirect("/")

    return render_template("login.html")

# REGISTER
@app.route("/register")
def register_user():
    return render_template("register.html")

# LOGOUT

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
