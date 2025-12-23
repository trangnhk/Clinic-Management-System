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
    role = None
    if current_user.is_authenticated:
        role = "patient"
        if isinstance(current_user, Nurse):
            role = "nurse"
        if isinstance(current_user, Cashier):
            role = "cashier"
        if isinstance(current_user, Administrator):
            role = "admin"
        elif isinstance(current_user, Doctor):
            role = "doctor"
    #     # elif isinstance(current_user, Cashier):
    #     #     return {"menu_bar": dao.load_menu_bar_cashier()}
    #     # elif isinstance(current_user, Administrator):
    #     #     return {"menu_bar": dao.load_menu_bar_admin()}
    #
    # # Default
    return {"menu_bar": dao.load_menu_bar(name=role)}

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



# PATIENT
@app.route('/appointment-ticket', methods=['get'])
@login_required
def get_appointment_ticket():
    aps = dao.get_appointment(patient_id=current_user.id, date=None)
    print(aps)
    return render_template("appointment_ticket.html", aps=aps)


@app.route('/online-appointment', methods=["get", "post"])
def create_online_appointment():
    if request.method == "GET":
        exam_date = request.args.get("exam_date")
        return render_template("patient/appointment.html", exam_date=exam_date, medicines=dao.load_medicines(),user=current_user,role="nurse")

    data = request.form

    # get exam date & url
    exam_date_str = request.form.get("exam_date")
    exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
    print(exam_date)


    # get/create examination list
    exam_list = dao.get_examinationlist_by_date(exam_date)
    # if not exam_list:
    #     exam_list = dao.create_examination_list(exam_date, current_user.id)


    # get/create patient
    patient = dao.get_or_create_patient(
        fullname=data.get("fullname"),
        medical_id=data.get("medical_id"),
        phone_number=data.get("phone_number"),
        dob=data.get("dob"),
        gender=data.get("gender"),
        address=data.get("address"),

    )

    # has patient yet?
    dao.add_patient_to_exam_list(exam_date, exam_list, patient)

    # allergy
    allergy_ids = data.getlist("medicine_allergy_ids")
    if allergy_ids:
        dao.add_patient_allergies(patient.id, allergy_ids)

    ap_id = str (dao.get_appointment(exam_date, patient_id=patient.id))
    return render_template('appointment_ticket.html', ap_id=ap_id)




# DOCTOR
@app.route('/doctor')
@login_required
def doctor_home_info():
    return render_template('home_info.html', user=current_user, role="doctor")

# CASHIER
# @app.route('/cashier')
# @login_required
# def cashier_home_info():
#     return render_template('home_info.html', user=current_user, role="cashier")

# ADMIN
# @app.route('/admin')
# @login_required
# def admin_home_info():
#     return render_template('home_info.html', user=current_user, role="admin")



if __name__ == "__main__":
    # app.register_blueprint()
    with app.app_context():
        app.run(debug=True)
