import uuid
from datetime import datetime, date
import cloudinary.uploader
from flask import json
from sqlalchemy import func, extract
from clinicsystem.models import User, Patient, Nurse, Doctor, Cashier, UserGender, Administrator, UserRole, \
    ExaminationList, Appointment, ExaminationStatus, Bill, BillStatus, Prescription, DetailPrescrip, Medicine, \
    AppointmentStatus, Allergy
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


def add_user(fullname,
             username,
             password,
             phone_number,
             dob=None,
             gender=None,
             avatar=None,
             address=None,
             medical_id=None) -> Patient:
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
                medical_id=medical_id
                )

    db.session.add(u)
    db.session.commit()

    return u


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


def load_menu_bar(name: str):
    if name.__eq__("patient") or not name:
        path = f"data/menu_bar.json"
    else:
        path = f"data/{name}/menu_bar.json"

    with open(path, encoding="utf-8") as f:
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


def get_or_create_patient(fullname: str, phone_number: str, dob, gender, address=None, medical_id=None) -> Patient:
    # Get patient?
    patient = Patient.query.filter_by(phone_number=phone_number).first()
    if patient:
        return patient

    # Create new patient
    password = "123"
    patient = add_user(fullname=fullname, username=phone_number, phone_number=phone_number, password=password, dob=dob,
                       gender=gender, address=address, medical_id=medical_id)

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
            if not ap_id:
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

    exam_list.confirm_list()

    db.session.commit()

    return exam_list


def load_medicines():
    from clinicsystem.models import Medicine
    medicines = Medicine.query.filter(Medicine.stock > 0).order_by(Medicine.name)
    return medicines.all()


def load_menu_bar_nurse():
    with open("data/nurse/menu_bar.json", encoding="utf-8") as f:
        return json.load(f)


# CASHIER
def get_waiting_bills():
    return Bill.query.filter(Bill.status == BillStatus.UNPAID).all()


def get_bill_detail(bill_id):
    bill = Bill.query.get(bill_id)
    if not bill: return None

    # Kiểm tra toa thuốc
    if not bill.prescrip: return None

    medicines = []
    if bill.prescrip.details:
        for d in bill.prescrip.details:
            medicines.append({
                'name': d.medicine.name,
                'unit': d.unit_name,
                'qty': d.quantity,
                'price': float(d.medicine.price),
                'amount': float(d.quantity * d.medicine.price)
            })

    return {
        'bill': bill,
        'patient': bill.prescrip.patient,
        'medicines': medicines
    }


def pay_bill(bill_id):
    b = db.session.get(Bill, bill_id)
    if b:
        b.update_status(BillStatus.PAYMENT)
        db.session.commit()
        return True
    return False


# ADMIN
def get_available_years():
    years = db.session.query(func.distinct(extract('year', Bill.created_date))) \
        .order_by(extract('year', Bill.created_date).desc()).all()

    return [int(y[0]) for y in years]



def overview_report(month, year):
    # 1. Xu hướng bệnh nhân (Appointments) - Lấy từ Bill cho chắc chắn ngày khám
    appointments = db.session.query(func.date(Bill.created_date), func.count(Bill.id)) \
        .filter(func.month(Bill.created_date) == month) \
        .filter(func.year(Bill.created_date) == year) \
        .group_by(func.date(Bill.created_date)).all()

    # 2. Xu hướng doanh thu
    revenue = db.session.query(func.date(Bill.created_date), func.sum(Bill.total)) \
        .filter(func.month(Bill.created_date) == month) \
        .filter(func.year(Bill.created_date) == year) \
        .group_by(func.date(Bill.created_date)).all()

    # 3. Xu hướng sử dụng thuốc
    medicines = db.session.query(func.date(Bill.created_date), func.sum(DetailPrescrip.quantity)) \
        .join(Prescription, Bill.prescrip_id == Prescription.id) \
        .join(DetailPrescrip, Prescription.id == DetailPrescrip.prescription_id) \
        .filter(func.month(Bill.created_date) == month) \
        .filter(func.year(Bill.created_date) == year) \
        .group_by(func.date(Bill.created_date)).all()

    labels = [d.strftime("%d/%m") for d, _ in appointments]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Appointment",
                "data": [v for _, v in appointments]
            },
            {
                "label": "Revenue",
                "data": [v for _, v in revenue]
            },
            {
                "label": "Medicines",
                "data": [v for _, v in medicines]
            }
        ]
    }


# Báo cáo doanh thu (Trang 2)
def revenue_report(month, year):
    rows = db.session.query(func.date(Bill.created_date),
                            func.count(Bill.id),
                            func.sum(Bill.total)) \
        .filter(func.month(Bill.created_date) == month) \
        .filter(func.year(Bill.created_date) == year) \
        .group_by(func.date(Bill.created_date)).all()

    chart_data = {
        "labels": [d.strftime("%d/%m") for d, _, _ in rows],
        "datasets": [
            {
                "label": "Revenue",
                "data": [float(v or 0) for _, _, v in rows]
            }
        ]
    }

    return {
        "table": rows,
        "chart": chart_data
    }


# Báo cáo sử dụng thuốc (Trang 3)
def medicine_report(month, year):
    rows = db.session.query(Medicine.name,
                            DetailPrescrip.unit_name,  # Lấy unit_name từ DetailPrescrip
                            func.sum(DetailPrescrip.quantity),
                            func.count(Prescription.id)) \
        .join(DetailPrescrip, Medicine.id == DetailPrescrip.medicine_id) \
        .join(Prescription, DetailPrescrip.prescription_id == Prescription.id) \
        .join(Bill, Bill.prescrip_id == Prescription.id) \
        .filter(func.month(Bill.created_date) == month) \
        .filter(func.year(Bill.created_date) == year) \
        .group_by(Medicine.id, DetailPrescrip.unit_name).all()

    return {
        "labels": [f"{name} ({unit})" for name, unit, qty, cnt in rows],
        "datasets": [
            {
                "label": "Total Quantity",
                "data": [qty for name, unit, qty, cnt in rows]
            }
        ]
    }


# DOCTOR
def get_waiting_patients(today=None):
    if not today:
        today = date.today()
        print(today)
    return (Appointment.query.join(ExaminationList)
            .filter(Appointment.status == AppointmentStatus.WAITING_EXAMINATION, ExaminationList.date == today)
            .order_by(Appointment.number.asc())
            .all()
        )

def get_patient_by_id(patient_id):
    return db.session.get(Patient, patient_id)

def get_medicines(kw=None):
    query = Medicine.query
    if kw:
        query = query.filter(Medicine.name.ilike(f"%{kw}%"))
    return query

def check_allergy(patient_id, medicine_id):
    # models.py: Allergy có patient_id (String) và medicine_id (Integer)
    return Allergy.query.filter_by(patient_id=patient_id, medicine_id=medicine_id).first()


# Lưu Phiếu Khám
def save_prescription(doctor_id, patient_id, symptom, diagnosis, medicine_list):
    try:
        pres_id = str(uuid.uuid4())[:20]

        pres = Prescription(
            id=pres_id,
            symptom=symptom,
            diagnosis=diagnosis,
            doctor_id=doctor_id,
            patient_id=patient_id
        )
        db.session.add(pres)


        for item in medicine_list:
            med_id = int(item['id'])
            qty = int(item['quantity'])
            instruction = item.get('cach_dung', '')

            med = Medicine.query.get(med_id)
            unit_name = med.unit.name if med.unit else "Viên"

            detail = DetailPrescrip(
                medicine_id=med_id,
                prescription_id=pres_id,
                quantity=qty,
                instruction=instruction,
                unit_name=unit_name
            )
            db.session.add(detail)

        db.session.commit()

        appointment = Appointment.query.filter_by(patient_id=patient_id, status=AppointmentStatus.WAITING_EXAMINATION).first()
        if appointment:
            appointment.update_status(AppointmentStatus.WAITING_PAYMENT)
            db.session.commit()

        return True

    except Exception as ex:
        print(f"LỖI LƯU PHIẾU: {ex}")
        db.session.rollback()
        return False

def get_patient_history(patient_id):
    return Prescription.query.filter_by(patient_id=patient_id).order_by(Prescription.created_date.desc()).all()

if __name__ == "__main__":
    with app.app_context():
        import_employees()
    #     get_appointment(date="2026-01-01", patient_id="patient8")
