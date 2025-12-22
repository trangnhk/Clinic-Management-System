from datetime import datetime
import cloudinary.uploader
from flask import json
from sqlalchemy import func
from clinicsystem.models import User, Patient, Nurse, Doctor, Cashier, UserGender, Administrator, UserRole, ExaminationList, Bill, Medicine, DetailPrescrip, Prescription, BillStatus, Unit
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

def add_user(fullname, username, password, phone_number, dob=None, gender=None, avatar = None):
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
             avatar=avatar)

    # if avatar:
    #     res = cloudinary.uploader.upload(avatar)
    #     print(res)
    #     u.avatar = res.get("secure_url")


    db.session.add(u)
    db.session.commit()

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
def get_examinationlist_by_date(date):
    day = date.date() if hasattr(date, "date") else date
    return ExaminationList.query.filter(func.date(ExaminationList.date) == day).first()

def load_menu_bar_nurse():
    with open("data/nurse/menu_bar.json", encoding="utf-8") as f:
        return json.load(f)

#CASHIER
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
    b = Bill.query.get(bill_id)
    if b:
        b.status = BillStatus.PAYMENT
        db.session.commit()
        return True
    return False

#ADMIN

# Báo cáo doanh thu (Trang 1)
def overview_report(month, year):
    # Sửa lỗi: Prescription của bạn không có created_date, phải join qua Bill

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

    return {
        'appointments': appointments,
        'revenue': revenue,
        'medicines': medicines
    }


# Báo cáo doanh thu (Trang 2)
def revenue_report(month, year):
    # Model của bạn: Bill có 'created_date', 'total'
    return db.session.query(func.date(Bill.created_date),
                            func.count(Bill.id),
                            func.sum(Bill.total))\
                     .filter(func.month(Bill.created_date) == month)\
                     .filter(func.year(Bill.created_date) == year)\
                     .group_by(func.date(Bill.created_date)).all()


# Báo cáo sử dụng thuốc (Trang 3)
def medicine_report(month, year):
    # Sửa lỗi: Model Medicine KHÔNG có 'unit_name', nó kết nối với bảng Unit qua 'unit_id'
    # Hoặc bạn có thể lấy 'unit_name' trực tiếp từ bảng DetailPrescrip (vì bạn có định nghĩa cột đó ở đó)
    return db.session.query(Medicine.name,
                            DetailPrescrip.unit_name, # Lấy unit_name từ DetailPrescrip cho đúng model
                            func.sum(DetailPrescrip.quantity),
                            func.count(Prescription.id))\
                     .join(DetailPrescrip, Medicine.id == DetailPrescrip.medicine_id)\
                     .join(Prescription, DetailPrescrip.prescription_id == Prescription.id)\
                     .join(Bill, Bill.prescrip_id == Prescription.id)\
                     .filter(func.month(Bill.created_date) == month)\
                     .filter(func.year(Bill.created_date) == year)\
                     .group_by(Medicine.id, DetailPrescrip.unit_name).all()

if __name__ == "__main__":
    with app.app_context():
        import_employees()

