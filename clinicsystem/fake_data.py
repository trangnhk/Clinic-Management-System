from datetime import datetime
import hashlib
import uuid
import random
from decimal import Decimal
from clinicsystem import app, db
from clinicsystem.models import (
    Patient,
    ExaminationList,
    ExaminationStatus,
    Nurse,
    Unit,
    Medicine,
    Allergy
)
from clinicsystem import app


# Hash password helper
def hash_password(password: str):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def create_fake_patients():
    patients = []

    patient_data = [
        {
            "fullname": "Nguyen Van A",
            "username": "patient_a",
            "password": "123456",
            "phone_number": "0900000001",
            "dob": datetime(2000, 1, 1),
            "gender": "MALE",
            "address": "Ho Chi Minh City"
        },
        {
            "fullname": "Tran Thi B",
            "username": "patient_b",
            "password": "123456",
            "phone_number": "0900000002",
            "dob": datetime(1998, 5, 12),
            "gender": "FEMALE",
            "address": "Hội An"
        },
        {
            "fullname": "Le Van C",
            "username": "patient_c",
            "password": "123456",
            "phone_number": "0900000003",
            "dob": datetime(1995, 9, 20),
            "gender": "MALE",
            "address": "Cần Thơ",
            "medical_id": "CTO0000009"
        }
    ]

    for data in patient_data:
        patient = Patient(
            fullname=data["fullname"],
            username=data["username"],
            password=hash_password(data["password"]),
            phone_number=data["phone_number"],
            dob=data["dob"],
            gender=data["gender"],
            address=data["address"]
        )
        db.session.add(patient)
        patients.append(patient)

    db.session.commit()
    return patients


def create_examination_list(date: datetime):
    # Lấy 1 nurse bất kỳ
    nurse = Nurse.query.first()
    if not nurse:
        raise Exception("YOU DON'T HAVE NURSE ACCOUNT!")

    exam = ExaminationList(
        date=date,
        status=ExaminationStatus.UNSUBMITTED,
        nurse_id=nurse.id
    )
    db.session.add(exam)
    db.session.commit()
    return exam


def add_patients_to_examination(exam: ExaminationList, patients):
    for patient in patients:
        exam.add_patient(patient)


def run():

    patients = create_fake_patients()

    exam_date = datetime(2025, 12, 30)
    exam = create_examination_list(exam_date)

    add_patients_to_examination(exam, patients)


def fake_units():
    unit_names = [
        "Viên",
        "Vỉ",
        "Chai"
    ]

    units = []
    for name in unit_names:
        if not Unit.query.filter_by(name=name).first():
            units.append(Unit(name=name))

    if units:
        db.session.add_all(units)
        db.session.commit()
    else:
        pass

def fake_medicines():
    units = Unit.query.all()

    if not units:
        return

    medicine_samples = [
        ("Paracetamol", 5000),
        ("Aspirin", 7000),
        ("Ibuprofen", 8000),
        ("Vitamin C", 3000),
        ("Amoxicillin", 12000),
        ("Cefixime", 25000),
        ("Metformin", 15000),
        ("Omeprazole", 10000),
        ("Loratadine", 6000),
        ("Prednisolone", 20000)
    ]

    medicines = []

    for name, price in medicine_samples:
        if Medicine.query.filter_by(name=name).first():
            continue

        medicines.append(
            Medicine(
                name=name,
                price=Decimal(str(price)),
                stock=random.randint(50, 300),
                unit_id=random.choice(units).id
            )
        )

    if medicines:
        db.session.add_all(medicines)
        db.session.commit()
    else:
        pass

def fake_allergies():
    patients = Patient.query.all()
    medicines = Medicine.query.all()

    if not patients or not medicines:
        return

    allergies = []

    for patient in patients:
        allergy_count = random.randint(0, 2)

        for _ in range(allergy_count):
            med = random.choice(medicines)

            if Allergy.query.filter_by(
                patient_id=patient.id,
                medicine_id=med.id
            ).first():
                continue

            allergies.append(
                Allergy(
                    id=str(uuid.uuid4())[:20],
                    level=random.randint(1, 3),
                    description="Dị ứng thuốc",
                    note=f"Dị ứng {med.name}",
                    patient_id=patient.id,
                    medicine_id=med.id
                )
            )

    if allergies:
        db.session.add_all(allergies)
        db.session.commit()
        print(f"✅ Đã tạo {len(allergies)} Allergy")
    else:
        print("ℹ️ Không có Allergy mới")

if __name__ == "__main__":
    with app.app_context():
        run()
        fake_units()
        fake_medicines()
        fake_allergies()
