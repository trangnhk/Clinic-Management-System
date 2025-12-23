from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, abort, jsonify
from flask_login import login_required, current_user

from clinicsystem import dao

doctor_page = Blueprint(
    'doctor',
    __name__,
    url_prefix="/doctor"
)

# Danh sách chờ khám
@doctor_page.route("/waiting-list", methods=["get"])
@login_required
def get_waiting_list():
    # Lấy danh sách từ DAO
    waiting_list = dao.get_waiting_patients()
    print(waiting_list)
    return render_template("doctor/waiting_list.html", waiting_list=waiting_list)

# Hiển thị trang Lập Phiếu Khám
@doctor_page.route("/prescription/<string:patient_id>")
@login_required
def lap_phieu_kham_view(patient_id):
    patient = dao.get_patient_by_id(patient_id)

    if not patient:
        abort(404)

    waiting_list = dao.get_waiting_patients()
    return render_template("doctor/prescription/index.html", waiting_list=waiting_list, patient=patient)


@doctor_page.route("/api/medicines")
@login_required
def search_medicines_api():
    kw = request.args.get("kw", "")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    query = dao.get_medicines(kw)

    medicines = query \
        .offset((page - 1) * limit) \
        .limit(limit) \
        .all()

    return jsonify({
        "data": [{
            "id": m.id,
            "name": m.name,
            "unit": m.unit.name if m.unit else "",
            "price": float(m.price),
            "stock": m.stock
        } for m in medicines],
        "has_more": len(medicines) == limit
    })

# 3. API: Kiểm tra dị ứng
@doctor_page.route("/api/check-allergy/<string:patientId>", methods=['POST'])
@login_required
def check_allergy_api(patient_id):
    data = request.json
    patient_id = data.get('patient_id')
    medicine_id = data.get('medicine_id')

    if not patient_id or not medicine_id:
        return jsonify({"is_allergic": False}), 400

    allergy = dao.check_allergy(patient_id, medicine_id)

    if allergy:
        return jsonify({
            "is_allergic": True,
            "description": allergy.description,
            "level": allergy.level
        })
    return jsonify({"is_allergic": False})

# Lưu phiếu khám
@doctor_page.route("/api/save-prescription/<string:patient_id>", methods=['POST'])
@login_required
def save_prescription_api(patient_id):
    data = request.json

    patient_id = data.get('patient_id')
    symptom = data.get('symptom')
    diagnosis = data.get('diagnosis')
    medicine_list = data.get('medicines')

    if not patient_id or not medicine_list:
        return jsonify({"status": 400, "msg": "Dữ liệu không hợp lệ"})

    doctor_id = "DOC-TEST"
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        doctor_id = current_user.id

    success = dao.save_prescription(doctor_id, patient_id, symptom, diagnosis, medicine_list)

    if success:

        return jsonify({"status": 200, "msg": "Lưu phiếu thành công!"})
    else:
        return jsonify({"status": 500, "msg": "Có lỗi xảy ra khi lưu!"})


@doctor_page.route("/api/patient-history/<string:patient_id>", methods=['POST'])
def get_patient_history_api(patient_id):
    data = request.get_json() or {}
    pid = data.get('patient_id') or patient_id
    if not pid:
        return jsonify([]), 400

    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return jsonify([]), 400

        # Lấy dữ liệu từ DB
    history_list = dao.get_patient_history(pid)

    results = []
    for h in history_list:
        results.append({
            "id": getattr(h, "id", ""),
            "date": getattr(h.created_date, "strftime", lambda fmt: "")("%d-%m-%Y") if h.created_date else "N/A",
            "doctor": getattr(getattr(h, "doctor", None), "name", "Ẩn danh"),
            "symptoms": getattr(h, "symptom", ""),
            "diagnosis": getattr(h, "diagnosis", "")
        })

    return jsonify(results)
