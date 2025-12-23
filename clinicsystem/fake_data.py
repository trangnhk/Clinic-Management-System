from datetime import datetime, date
import hashlib
import uuid
import random
from decimal import Decimal
from clinicsystem import app, db, dao
from clinicsystem.models import (
    Patient,
    ExaminationList,
    ExaminationStatus,
    Nurse,
    Unit,
    Medicine,
    Allergy, DetailPrescrip, Appointment, AppointmentStatus, Bill, BillStatus, Prescription, Cashier, Doctor
)
from clinicsystem import app
from flask import json

# Hash password helper
def hash_password(password: str):
    return hashlib.md5(password.encode("utf-8")).hexdigest()


def create_fake_patients():
    with open(f"data/fake_data.json", encoding="utf-8") as f:
        data = json.load(f)

    patients = data.get("patient_data", [])
    created_patient = []

    for patient in patients:
        medical_id = patient.get("medical_id")
        if not medical_id:
            medical_id = None
        if Patient.query.filter_by(username=patient["username"]).first():
            continue

        p = dao.add_user(
            fullname=patient["fullname"],
            username=patient["username"],
            password=patient["password"],
            phone_number=patient["phone_number"],
            dob=patient["dob"],
            gender=patient["gender"],
            address=patient["address"],
            medical_id=medical_id
        )
        created_patient.append(p)

    return created_patient


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

    exam_date = datetime(2025, 12, 30).date()
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
        allergy_count = random.randint(0, 4)

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
        print(f"Đã tạo {len(allergies)} Allergy")
    else:
        print("Không có Allergy mới")

def fake_prescriptions():
    patients = Patient.query.all()
    doctor = Doctor.query.first()
    medicines = Medicine.query.all()

    if not patients or not doctor or not medicines:
        return

    prescriptions = []

    for patient in patients:
        pres = Prescription(
            id=str(uuid.uuid4())[:20],
            symptom="Sốt, đau đầu",
            diagnosis="Cảm cúm",
            doctor_id=doctor.id,
            patient_id=patient.id
        )

        db.session.add(pres)
        db.session.flush()  # để có pres.id

        # mỗi đơn 1–3 thuốc
        for med in random.sample(medicines, random.randint(1, 3)):
            detail = DetailPrescrip(
                prescription_id=pres.id,
                medicine_id=med.id,
                quantity=random.randint(1, 5),
                unit_name=med.unit.name,
                instruction="Uống sau ăn"
            )
            db.session.add(detail)

        prescriptions.append(pres)

    db.session.commit()
    return prescriptions

def fake_bills():
    prescriptions = Prescription.query.filter(~Prescription.bill.has()).all()
    cashier = Cashier.query.first()

    if not prescriptions or not cashier:
        return

    bills = []

    for pres in prescriptions:
        medicine_fee = pres.cal_medicine_fee()

        bill = Bill(
            id=str(uuid.uuid4())[:20],
            medical_fee=Decimal("100000"),
            medicine_fee=medicine_fee,
            total=Decimal("100000") + medicine_fee,
            status=random.choice(list(BillStatus)),
            prescrip_id=pres.id,
            cashier_id=cashier.id,
            created_date=datetime.now().date()
        )

        bills.append(bill)

    db.session.add_all(bills)
    db.session.commit()

def randomize_appointment_status():
    appointments = Appointment.query.all()
    for ap in appointments:
        ap.status = random.choice(list(AppointmentStatus))
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        run()
        fake_units()
        fake_medicines()
        fake_allergies()
        fake_prescriptions()
        fake_bills()
        # randomize_appointment_status()

