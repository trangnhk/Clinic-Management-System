from datetime import datetime, date
import cloudinary.uploader
from flask import json
from sqlalchemy import func
from clinicsystem.models import User, Patient, Nurse, Doctor, Cashier, UserGender, Administrator, UserRole, \
    ExaminationList, Appointment, ExaminationStatus
from clinicsystem import app, db
import hashlib


# USER
def auth_account(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()

    # 1. Try Patient
    user = Patient.query.filter_by(username=username, password=password).first()
    if user:
        return user

    # 2. Try Nurse
    user = Nurse.query.filter_by(username=username, password=password).first()
    if user:
        return user

    # 3. Try Doctor
    user = Doctor.query.filter_by(username=username, password=password).first()
    if user:
        return user

    # 4. Try Cashier
    user = Cashier.query.filter_by(username=username, password=password).first()
    if user:
        return user

    # 5. Try Administrator
    user = Administrator.query.filter_by(username=username, password=password).first()
    if user:
        return user

    return None

# generate user_id
def generate_role_id(prefix: str, model):
    pattern = f"{prefix}%"

    latest = (
        db.session.query(model.id)
        .filter(model.id.like(pattern))
        .order_by(model.id.desc())
        .first()
    )

    if latest:
        number = int(latest[0].replace(prefix, "")) + 1
    else:
        number = 1

    return f"{prefix}{number}"

def get_user_id(user_id):
    return db.session.get(User, user_id)

def get_user_by_username(username):
     return User.query.filter_by(username=username).first()

def get_user_by_phone(phone_number):
     return User.query.filter_by(phone_number=phone_number).first()

def add_user(fullname, username, password, phone_number, dob=None, gender=None, avatar = None, address=None, medical_id=None) -> Patient:
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    if isinstance(dob, str):
        dob = datetime.strptime(dob, "%Y-%m-%d").date()

    if isinstance(gender, str):
        gender = UserGender.MALE if gender.upper() == "MALE" else UserGender.FEMALE



    u = Patient(fullname=fullname,
             username=username,
             password=password,
             phone_number=phone_number,
             dob=dob,
             gender=gender,
             avatar=avatar,
            address=address,
            medical_id=medical_id)

    # if avatar:
    #     res = cloudinary.uploader.upload(avatar)
    #     print(res)
    #     u.avatar = res.get("secure_url")


    db.session.add(u)
    db.session.commit()

    return  u

# DEFAULT

def import_employees():
    with open("data/employee_accounts.json", encoding="utf-8") as f:
        data = json.load(f)

    employees = data.get("employees", [])

    for emp in employees:

        gender = UserGender.MALE if emp["gender"] == "MALE" else UserGender.FEMALE
        password = hashlib.md5(emp["password"].encode("utf-8")).hexdigest()
        dob = datetime.strptime(emp["dob"], "%Y-%m-%d")

        role = emp["role"].upper()

        # Has username in table?
        if User.query.filter_by(username=emp["username"]).first():
            print("USERNAME EXIST, SKIP: ", emp['username'])
            continue

        if role == "NURSE":
            user = Nurse(
                fullname=emp["fullname"],
                username=emp["username"],
                password=password,
                phone_number=emp["phone_number"],
                dob=dob,
                gender=gender,
                role=UserRole.EMPLOYEE,
                avatar=emp.get("avatar")
            )

        elif role == "DOCTOR":
            user = Doctor(
                fullname=emp["fullname"],
                username=emp["username"],
                password=password,
                phone_number=emp["phone_number"],
                dob=dob,
                gender=gender,
                specialist=emp.get("specialist", "General"),
                role=UserRole.EMPLOYEE,
                avatar=emp.get("avatar")
            )

        elif role == "CASHIER":
            user = Cashier(
                fullname=emp["fullname"],
                username=emp["username"],
                password=password,
                phone_number=emp["phone_number"],
                dob=dob,
                gender=gender,
                role=UserRole.EMPLOYEE,
                avatar=emp.get("avatar")
            )

        elif role == "ADMIN":
            user = Administrator(
                fullname=emp["fullname"],
                username=emp["username"],
                password=password,
                phone_number=emp["phone_number"],
                dob=dob,
                gender=gender,
                role=UserRole.EMPLOYEE,
                avatar=emp.get("avatar")
            )

        db.session.add(user)

    db.session.commit()
    print("Import employees completed!")

def load_menu_bar():
    with open("data/menu_bar.json", encoding="utf-8") as f:
        return json.load(f)

# NURSE
def get_examinationlist_by_date(date) -> ExaminationList:
    day = date.date() if hasattr(date, "date") else date
    return ExaminationList.query.filter(func.date(ExaminationList.date) == day).first()

def create_examination_list(date: date, nurse_id=None):
    # if isinstance(date, str):
    #     date = datetime.strptime(date, "%Y-%m-%d")
    exam_list = ExaminationList(date=date, nurse_id=nurse_id, status=ExaminationStatus.UNSUBMITTED)

    db.session.add(exam_list)
    db.session.commit()
    return exam_list

def get_policy_value(name: str) -> int:
    from clinicsystem.models import Policy
    policy = Policy.query.filter_by(name=name).first()
    return int(policy.number) if policy else 40

def get_or_create_patient(fullname: str, phone_number: str, dob, gender, address=None, medical_id=None)->Patient:
    # Get patient?
    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if patient:
        return patient

    # Create new patient
    password = "123"
    patient = add_user(fullname=fullname, username=phone_number, phone_number=phone_number, password=password, dob=dob, gender=gender, address=address, medical_id=medical_id)

    return patient


def add_patient_to_exam_list(date: date, exam_list: ExaminationList, patient: Patient):

    if not exam_list:
        exam_list = create_examination_list(date=date)

    if exam_list.status != ExaminationStatus.UNSUBMITTED:
        raise ValueError("Examination list already submitted")

    if any(ap.patient_id == patient.id for ap in exam_list.appointments):
        raise ValueError("Patient already in examination list")

    # Check policy
    max_patients = get_policy_value("max patient per day")
    if len(exam_list.appointments) >= max_patients:
        raise ValueError("Exceed maximum patient limit")

    exam_list.add_patient(patient)

    #
    # appointment = Appointment(
    #     patient_id=patient.id,
    #     examination_id=exam_list.id,
    #     number=len(exam_list.appointments) + 1
    # )

    # db.session.add(appointment)
    # db.session.commit()

    # return appointment

def add_patient_allergies(patient_id=str, medicine_ids=list[int]):
    patient = Patient.query.get(patient_id)
    if not patient:
        raise ValueError("Not found patient")

    if not medicine_ids:
        return

    from clinicsystem.models import Medicine

    medicines = Medicine.query.filter(Medicine.id.in_(medicine_ids)).all()

    patient.medicines = medicines
    db.session.commit()

def remove_appointment(appointment_id):
    ap = Appointment.query.get(appointment_id)
    if not ap:
        raise ValueError("Appointment not found")

    exam_list = ap.examinationList
    db.session.delete(ap)
    db.session.commit()

    return exam_list

def get_appointment(date, patient_id):
    if not date:
        exam_list = ExaminationList.query.all()

        aps = []
        for ex in exam_list:
            ap_id = Appointment.query.filter_by(examination_id=ex.id, patient_id=patient_id).first()
            if ap_id != None:
                aps.append(ap_id)

        return aps

    else:
        exam_list = ExaminationList.query.filter(func.date(ExaminationList.date) == date).first()
        ap_id = Appointment.query.filter_by(examination_id=exam_list.id, patient_id=patient_id).first()
        return ap_id


def submit_examination_list(date, nurse_id):
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()

    exam_list = ExaminationList.query.filter(
        func.date(ExaminationList.date) == date
    ).first()

    if not exam_list:
        raise ValueError("Examination list not found")

    if exam_list.status == ExaminationStatus.SUBMIITED:
        return exam_list

    exam_list.status = ExaminationStatus.SUBMIITED
    exam_list.nurse_id = nurse_id
    db.session.commit()

    return exam_list

def load_medicines():
    from clinicsystem.models import Medicine
    medicines = Medicine.query.filter(Medicine.stock > 0).order_by(Medicine.name)
    return medicines.all()

def load_menu_bar_nurse():
    with open("data/nurse/menu_bar.json", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    with app.app_context():
    #     import_employees()
        get_appointment(date="2026-01-01", patient_id="patient8")


