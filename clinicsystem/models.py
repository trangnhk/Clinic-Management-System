from clinicsystem import app, db
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum as RoleEnum

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


class Employee(User):
    __abstract__ = True

    salary = Column(Float, nullable=False, default=5000000)

class Nurse(Employee):
    pass

class Doctor(Employee):
    specialist = Column(String(50), nullable=False, default="General Practitioner")

class Cashier(Employee):
    pass

class Administrator(Employee):
    pass

if __name__ == '__main__':
    with app.app_context():
        db.create_all()