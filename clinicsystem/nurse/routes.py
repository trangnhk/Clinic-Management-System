from datetime import datetime, timedelta

from flask import Blueprint, render_template, abort, request, jsonify, redirect
from jinja2 import TemplateNotFound
from flask_login import login_required, current_user
from clinicsystem.models import ExaminationList, ExaminationStatus, Appointment

from clinicsystem import dao

nurse_page = Blueprint(
    'nurse',
    __name__,
    url_prefix="/nurse"
)

# /nurse
@nurse_page.route("/")
@login_required
def nurse_home_info():
    try:
        return render_template('home_info.html', user=current_user, role="nurse")
    except TemplateNotFound:
        abort(404)

@nurse_page.route("/examination-list", methods=["get"])
@login_required
def examination_list():

    return render_template('nurse/examinationList.html', user=current_user, role="nurse")

@nurse_page.route("/api/examination-list", methods=["get"])
@login_required
def get_examination_list():
    date = request.args.get("date")
    print(date)

    if not date:
        return jsonify({
            "error": "Missing 'date'"
        }), 400

    try:
        exam_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "error": "Invalid date format. Expected YYYY-MM-DD"
        }), 400


    exam_list = ExaminationList.query.filter(ExaminationList.date == exam_date).first()

    if not exam_list:
        return jsonify({
            "exists": False,
            "status": "UNSUBMITTED",
            "patients": []
        })

    return jsonify({
        "exists": True,
        "status": exam_list.status.name,
        "patients": [
            {
                "appointment_id": ap.id,
                "patient_id": ap.patient.id,
                "fullname": ap.patient.fullname,
                "medical_id": ap.patient.medical_id,
                "dob": ap.patient.dob.strftime("%d-%m-%Y"),
                "phone": ap.patient.phone_number,
                "address": ap.patient.address,
                "number": ap.number
            }
            for ap in exam_list.appointments
        ]
    })


@nurse_page.route("/api/examination-list/<appointment_id>", methods=["delete"])
@login_required
def delete_patient(appointment_id):
    try:
        exam_list = dao.remove_appointment(appointment_id)

        return jsonify({
            # "total": len(exam_list.appointments),
            "status": exam_list.status.name
        })
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

@nurse_page.route("/api/examination-list/submit", methods=["post"])
@login_required
def submit_examination_list():
    date = request.json.get("date")
    try:
        dao.submit_examination_list(date, nurse_id=current_user.id)

        return jsonify({"status": 200})
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400


@nurse_page.route("/add-patient", methods=["get", "post"])
@login_required
def add_patient():
    if request.method == "GET":
        exam_date = request.args.get("exam_date")
        return render_template("nurse/addPatient.html", exam_date=exam_date, medicines=dao.load_medicines(),user=current_user,role="nurse")

    data = request.form

    # get exam date & url
    exam_date_str = request.form.get("exam_date")
    exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
    print(exam_date)
    next_url = data.get("next")

    if not next_url or next_url.strip().lower() == "none":
        next_url = None

    # get/create examination list
    exam_list = dao.get_examinationlist_by_date(exam_date)
    if not exam_list:
        exam_list = dao.create_examination_list(exam_date, current_user.id)

    if exam_list.status != ExaminationStatus.UNSUBMITTED:
        abort(403, "Examination list already SUBMITTED")

    # get/create patient
    patient = dao.get_or_create_patient(
        fullname=data.get("fullname"),
        medical_id=data.get("medical_id"),
        phone_number=data.get("phone_number"),
        dob=data.get("dob"),
        gender=data.get("gender"),
        address=data.get("address")
    )

    # has patient yet?
    dao.add_patient_to_exam_list(exam_date, exam_list, patient)

    # allergy
    allergy_ids = data.getlist("medicine_allergy_ids")
    if allergy_ids:
        dao.add_patient_allergies(patient.id, allergy_ids)

    return redirect(
        next_url
        if next_url
        else f"/nurse/examination-list?date={exam_date.strftime('%Y-%m-%d')}"
    )


