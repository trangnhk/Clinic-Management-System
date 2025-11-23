from clinicsystem import app, db
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship, mapped_column
from enum import Enum as RoleEnum
from datetime import datetime

class UserRole(RoleEnum):
    PATIENT = 1
    EMPLOYEE = 2

class UserGender(RoleEnum):
    MALE = 1
    FEMALE = 2

class User(db.Model):
    __abstract__ = True

    id = Column(String(30), unique=True, primary_key=True, nullable=False)
    fullname = Column(String(50), nullable=False)
    username = Column(String(30), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    phone_number = Column(String(10), nullable=False, unique=True)
    dob = Column(DateTime, nullable=False)
    gender = Column(Enum(UserGender), nullable=False)
    address = Column(String(100), default="Ho Chi Minh City")
    role = Column(Enum(UserRole), default=UserRole.PATIENT)

    def __str__(self):
        return self.fullname

    def login(self):
        pass

    def logout(self):
        pass

    def update_info(self):
        pass

class Patient(User):
    medical_id = Column(String(30))
    appointments = relationship('Appointment', backref='patient', lazy=True)
    prescrips = relationship('Prescription', backref='patient', lazy=True)
    allergies = relationship('Allergy', backref='patient', lazy=True)


class Employee(User):
    __abstract__ = True

    salary = Column(Float, nullable=False, default=5000000.0)

class Nurse(Employee):
    examinations = relationship('ExaminationList', backref='nurse', lazy=True)


class Doctor(Employee):
    specialist = Column(String(50), nullable=False, default="General Practitioner")
    prescrips = relationship('Prescription', backref='doctor', lazy=True)

class Cashier(Employee):
    bills = relationship('Bill', backref='cashier', lazy=True)

class Policy(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    number = Column(Float)
    description = Column(String(50), nullable=False)

    def update(self, new_name: str = None, new_number: float = None):
        if new_name is not None:
            self.name = new_name
        if new_number is not None:
            self.number = new_number

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Commit failed because: {e}")
            return False

    def get_number(self, name):
        return self.number

class Administrator(Employee):
    def change_policy(self, policy_name: str = None, policy_id: int = None, new_number: float = None) -> bool:
        policy = Policy.query.get(policy_id)
        if not policy:
            raise ValueError(f"CAN NOT FIND POLICY_ID {policy_id}")

        success = policy.update(new_name=policy_name, new_number=new_number)
        return success

    def add_medicine(self, medicine) -> bool:
        pass

    def destroy_medicine(self, medicine) -> bool:
        pass

    def update_medicine(self, medicine) -> bool:
        pass

    def add_unit(self, unit) -> bool:
        pass

    def destroy_unit(self, unit) -> bool:
        pass

    def update_unit(self, unit) -> bool:
        pass

    def get_report(self, month, year) -> []:
        pass

    def get_medicine_report(self, month, year) -> []:
        pass


class ExaminationList(db.Model):
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.now)
    appointments = relationship('Appointment', backref='examinationList', lazy=True)
    nurse_id = Column(String(30), ForeignKey(Nurse.id), nullable=False)


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
    examination_id = Column(Integer, ForeignKey(ExaminationList.id), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING_CONFIRM)
    patient_id = Column(String(30), ForeignKey(Patient.id), nullable=False)



class BillStatus(RoleEnum):
    UNPAID = 1
    PAYMENT = 2
    CANCELLED = 3

class Bill(db.Model):
    id = Column(String(20), nullable=False, unique=True, primary_key=True)
    medical_fee = Column(Float, nullable=False, default=100000.0)
    medicine_fee = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.UNPAID)
    prescription = relationship('Prescription', back_populates='bill', uselist=False)
    cashier_id = Column(String(30), ForeignKey(Cashier.id), nullable=False)
    def __init__(self):
        pass

    def cal_total(self):
        self.total = self.medical_fee + self.medicine_fee
        return self.total

class Prescription(db.Model):
    id = Column(String(20), unique=True, nullable=False, primary_key=True)
    symptom = Column(String(150), nullable=False)
    diagnosis = Column(String(150), nullable=False)

    doctor_id = Column(String(30), ForeignKey(Doctor.id), nullable=False)
    bill_id = Column(String(20), ForeignKey(Bill.id), unique=True, nullable=False)
    bill = relationship(Bill, back_populates='prescription')
    patient_id = Column(String(30), ForeignKey(Patient.id), nullable=False)
    details = relationship('DetailPrescrip', back_populates='prescription')

class Unit(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    medicines = relationship('Medicine', backref='unit', lazy=True)

    def __str__(self):
        return self.name

class Medicine(db.Model):
    id = Column(Integer, unique=True, nullable=False, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    unit_id = Column(Integer, ForeignKey(Unit.id), nullable=False)
    details = relationship('DetailPrescrip', back_populates='medicine')


class DetailPrescrip(db.Model):
    __tablename__ = "detail_prescrip"

    medicine_id = Column(Integer, ForeignKey(Medicine.id), primary_key=True)
    prescription_id = Column(String(20), ForeignKey(Prescription.id), primary_key=True)

    quantity = Column(Integer, nullable=False, default=1)
    unit_name = Column(String(20), nullable=False)
    instruction = Column(String(150), nullable=False)

    medicine = relationship(Medicine, back_populates="details")
    prescription = relationship(Prescription, back_populates="details")

    def cal_price(self):
        if self.medicine and self.medicine.price is not None:
            return self.quantity * self.medicine.price
        return 0.0

class Allergy(db.Model):
    id = Column(String(20), unique=True, nullable=False, primary_key=True)
    level = Column(Integer, nullable=False)
    description = Column(String(30), nullable=False)
    note = Column(String(30))

    patient_id = Column(String(20), ForeignKey(Patient.id), nullable=True)
    medicine_id = Column(Integer, ForeignKey(Medicine.id), nullable=True)

    def is_allergic(self, patient, medicine):
        pass

    def get_warning(self):
        pass



if __name__ == '__main__':
    with app.app_context():
        db.create_all()