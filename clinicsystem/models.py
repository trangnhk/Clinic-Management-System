import hashlib

from clinicsystem import db, app
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, DECIMAL, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from enum import Enum as RoleEnum
from datetime import datetime, date
from decimal import Decimal
from flask_login import UserMixin
import uuid

class UserRole(RoleEnum):
    PATIENT = 1
    EMPLOYEE = 2

class UserGender(RoleEnum):
    MALE = 1
    FEMALE = 2

class User(db.Model, UserMixin):
    # __abstract__ = True
    __tablename__ = "users"

    id = Column(String(40), unique=True, primary_key=True, nullable=False)
    fullname = Column(String(50), nullable=False)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    phone_number = Column(String(10), nullable=False, unique=True)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(UserGender), nullable=False)
    address = Column(String(100), default="Ho Chi Minh City")
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    avatar = Column(String(150), nullable=True, default="https://res.cloudinary.com/dxfbpkmen/image/upload/v1764768698/profile_efyd9k.png")

    def __str__(self):
        return self.fullname

    def update_password(self, new_password: str):
        self.password = hashlib.md5(new_password.encode('utf-8')).hexdigest()
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

class Patient(User):
    __tablename__ = "patient"

    medical_id = Column(String(30))
    id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)

    # One-to-Many with Appointment
    appointments = relationship('Appointment', backref='patient', lazy=True)

    # One-to-Many with Prescription
    prescrips = relationship('Prescription', backref='patient', lazy=True)

    # One-to-Many with Allergy
    allergies = relationship('Allergy', backref='patient', lazy=True)

    def __init__(self, *args, **kwargs):
        from clinicsystem import dao
        kwargs["id"] = dao.generate_role_id("patient", Patient)

        super().__init__(*args, **kwargs)


class EmployeeMixin:
    # __tablename__ = "employee"
    # __abstract__ = True

    # id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    salary = Column(DECIMAL(10,3), nullable=False, default=5000000.0)


class Nurse(User,EmployeeMixin):
    __tablename__ = "nurse"
    id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    # One-to-many with ExaminationList
    examinations = relationship('ExaminationList', backref='nurse', lazy=True)

    def __init__(self, *args, **kwargs):
        from clinicsystem import dao
        kwargs["id"] = dao.generate_role_id("nurse", Nurse)
        super().__init__(*args, **kwargs)

class Doctor(User, EmployeeMixin):
    __tablename__ = "doctor"
    id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)

    specialist = Column(String(50), nullable=False, default="General Practitioner") # default: Bsi da khoa

    # One-to-many with Prescription
    prescrips = relationship('Prescription', backref='doctor', lazy=True)

    def __init__(self, *args, **kwargs):
        from clinicsystem import dao
        kwargs["id"] = dao.generate_role_id("doctor", Doctor)
        super().__init__(*args, **kwargs)

    # def get_examination_list(self):
    #     pass
    #
    # def create_prescription(self):
    #     pass
    #
    # def view_medical_history(self):
    #     pass

class Cashier(User, EmployeeMixin):
    __tablename__ = "cashier"
    id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)
    # One-to-many with Bill
    bills = relationship('Bill', backref='cashier', lazy=True)

    def __init__(self, *args, **kwargs):
        from clinicsystem import dao
        kwargs["id"] = dao.generate_role_id("cashier", Cashier)
        super().__init__(*args, **kwargs)

class Policy(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    number = Column(DECIMAL(10,3))
    description = Column(String(50), nullable=False)

    def update(self, new_name: str = None, new_number: float = None):
        if new_name is not None:
            self.name = new_name
        if new_number is not None:
            self.number = Decimal(str(new_number))

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Commit failed because: {e}")
            return False

    def get_number(self, name):
        return self.number

class Administrator(User, EmployeeMixin):
    __tablename__ = "administrator"
    id = Column(String(40), ForeignKey(User.id), primary_key=True, unique=True, nullable=False)

    def __init__(self, *args, **kwargs):
        from clinicsystem import dao
        kwargs["id"] = dao.generate_role_id("admin", Administrator)
        super().__init__(*args, **kwargs)

    # def change_policy(self, policy_name: str = None, policy_id: int = None, new_number: float = None) -> bool:
    #     policy = Policy.query.get(policy_id)
    #     if not policy:
    #         raise ValueError(f"CAN NOT FIND POLICY_ID {policy_id}")
    #
    #     success = policy.update(new_name=policy_name, new_number=new_number)
    #     return success

    # def add_medicine(self, medicine) -> bool:
    #     pass
    #
    # def destroy_medicine(self, medicine) -> bool:
    #     pass
    #
    # def update_medicine(self, medicine) -> bool:
    #     pass
    #
    # def add_unit(self, unit) -> bool:
    #     pass
    #
    # def destroy_unit(self, unit) -> bool:
    #     pass
    #
    # def update_unit(self, unit) -> bool:
    #     pass
    #
    # def get_report(self, month, year) -> []:
    #     pass
    #
    # def get_medicine_report(self, month, year) -> []:
    #     pass

class ExaminationStatus(RoleEnum):
    UNSUBMITTED = 1
    SUBMIITED = 2

class ExaminationList(db.Model):
    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    date = Column(Date, nullable=False, default=datetime.date, unique=True)
    status = Column(Enum(ExaminationStatus), nullable=False, default=ExaminationStatus.UNSUBMITTED)

    # One-to-many with Appointment
    appointments = relationship('Appointment', backref='examinationList', lazy=True)

    # Many-to-One with Nurse
    nurse_id = Column(String(30), ForeignKey(Nurse.id), nullable=True)

    def max_patients(self):
        import dao
        return dao.get_policy_value("MAX_EXAMINATION_PATIENT")

    def is_full(self):
        return len(self.appointments) >= self.max_patients()

    def add_patient(self, patient: Patient):
        if self.status != ExaminationStatus.UNSUBMITTED:
            raise ValueError("Danh sách đã nộp")

        if self.is_full():
            raise ValueError("Danh sách đã đủ số lượng quy định")

        number = len(self.appointments) + 1
        appointment = Appointment(
            id=str(uuid.uuid4())[:20],
            number=number,
            patient_id=patient.id,
            examination_id=self.id,
            status=AppointmentStatus.PENDING_CONFIRM
        )
        db.session.add(appointment)
        db.session.commit()

    def confirm_list(self):
        if self.status.__eq__(ExaminationStatus.SUBMIITED):
            for a in self.appointments:
                a.update_status(AppointmentStatus.WAITING_EXAMINATION)
    # def is_successfully_add_patient(self, patient: Patient) -> bool:
    #     pass
    #
    # def is_successfully_deleted(self, patient: Patient) -> bool:
    #     pass
    # """
    # def get_number_of_patients(self):
    #     pass
    # """
    #
    # def is_full(self) -> bool:
    #     pass


class AppointmentStatus(RoleEnum):
    PENDING_CONFIRM = 1
    WAITING_EXAMINATION = 2
    IN_EXAMINATION = 3
    WAITING_PAYMENT = 4
    COMPLETED = 5
    CANCELLED = 6
class Appointment(db.Model):
    id = Column(String(20), unique=True, nullable=False, primary_key=True)
    number = Column(Integer, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING_CONFIRM)

    # Many-to-One with ExaminationList
    examination_id = Column(Integer, ForeignKey(ExaminationList.id), nullable=False)

    # Many-to-One with Patient
    patient_id = Column(String(30), ForeignKey(Patient.id), nullable=False)

    __table_args__ = (UniqueConstraint("examination_id", "number"),)

    def update_status(self, new: AppointmentStatus):
        self.status = new

    # def __str__(self):
    #     return self.id

class BillStatus(RoleEnum):
    UNPAID = 1
    PAYMENT = 2
    CANCELLED = 3

class Bill(db.Model):
    id = Column(String(20), nullable=False, unique=True, primary_key=True)
    medical_fee = Column(DECIMAL(10,3), nullable=False, default=100000.000)
    medicine_fee = Column(DECIMAL(10,3), default=0.0)
    total = Column(DECIMAL(15,3), nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.UNPAID)
    created_date = Column(Date, nullable=False, default=datetime.date)

    # One-to-one with Bill
    prescrip_id = Column(String(20), ForeignKey('prescription.id'), unique=True, nullable=False)
    prescrip = relationship('Prescription', back_populates='bill')

    # Many-to-One with Cashier
    cashier_id = Column(String(30), ForeignKey(Cashier.id), nullable=False)

    def cal_total(self):
        self.total = self.medical_fee + self.medicine_fee
        return self.total

    def update_status(self, new_billstatus: BillStatus):
        self.status = new_billstatus

    def update_date(self, new_date: Date):
        self.created_date = new_date

class Prescription(db.Model):
    id = Column(String(20), unique=True, nullable=False, primary_key=True)
    symptom = Column(String(150), nullable=False)
    diagnosis = Column(String(150), nullable=False)
    created_date = Column(Date, nullable=False, default=date.today())

    # Many-to-one with Doctor
    doctor_id = Column(String(30), ForeignKey(Doctor.id), nullable=False)

    # One-to-One with Bill
    bill = relationship('Bill', uselist=False, back_populates='prescrip')

    # Many-to-one with Patient
    patient_id = Column(String(30), ForeignKey(Patient.id), nullable=False)

    # Many-to-Many with Prescription
    details = relationship('DetailPrescrip', back_populates='prescription')

    def update_clinical_info(self, symptom: str = None, diagnosis: str = None):
        self.symptom = symptom
        self.diagnosis = diagnosis



    # def add_medicine(self, detail):
    #     self.details

    def cal_medicine_fee(self) -> Decimal:
        if not self.details:
            return Decimal('0.0')

        total = sum(detail.cal_price() for detail in self.details)
        return total


class Unit(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)

    # One-to-Many with Medicine
    medicines = relationship('Medicine', backref='unit', lazy=True)

    def __str__(self):
        return self.name

class Medicine(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(DECIMAL(10,3), nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # Many-to-one with Unit
    unit_id = Column(Integer, ForeignKey(Unit.id), nullable=False)

    # Many-to-many with Medicine
    details = relationship('DetailPrescrip', back_populates='medicine')

    # One-to-Many with Allergy
    allergies = relationship('Allergy', backref='medicine', lazy=True)

    def is_in_stock(self, stock: int) -> bool:
        return self.stock - stock >= 0

    def get_price(self) -> Decimal:
        return self.price

# Many-to-Many (Medicine - Prescription)
class DetailPrescrip(db.Model):
    __tablename__ = "detail_prescrip"

    # Many-to-Many ForeignKey
    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True)
    prescription_id = Column(String(20), ForeignKey(Prescription.id), primary_key=True)

    quantity = Column(Integer, nullable=False, default=1)
    unit_name = Column(String(20), nullable=False)
    instruction = Column(String(150), nullable=False)

    medicine = relationship(Medicine, back_populates="details")
    prescription = relationship(Prescription, back_populates="details")

    def cal_price(self) -> Decimal:
        if self.medicine and self.medicine.price is not None:
            return self.quantity * self.medicine.price
        return Decimal('0.0')

class Allergy(db.Model):
    id = Column(String(20), unique=True, nullable=False, primary_key=True)
    level = Column(Integer, nullable=False)
    description = Column(String(30), nullable=False)
    note = Column(String(30))

    # Many-to-One with Patient
    patient_id = Column(String(20), ForeignKey(Patient.id), nullable=True)

    # Many-to-One with Medicine
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=True)

    # def is_allergic(self, patient_id: str = None, medicine_id: str = None) -> bool:
    #     allergy = Allergy.query.filter_by(patient_id=patient_id, medicine_id=medicine_id).first()
    #
    #     return allergy is not None
    #
    # def get_warning(self, patient_id: str = None, medicine_id: str = None) -> str:
    #     if self.is_allergic(patient_id=patient_id, medicine_id=medicine_id):
    #         return f"PATIENT {self.patient_id.name} HAS ALLERGY WITH {self.medicine_id.name}"
    #     return f"DON'T HAVING ANY ALLERGIES"

if __name__ == '__main__':
    # pass
    with app.app_context():
        db.create_all()
