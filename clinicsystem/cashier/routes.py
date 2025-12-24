from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound

from clinicsystem import dao

cashier_page = Blueprint(
    'cashier',
    __name__,
    url_prefix="/cashier"
)

# cashier
@cashier_page.route("/")
@login_required
def cashier_home_info():
    try:
        return render_template('home_info.html', user=current_user, role="cashier")
    except TemplateNotFound:
        abort(404)

@cashier_page.route('/payment')
@login_required
def cashier_payment():
    waiting_list = dao.get_waiting_bills()
    return render_template('cashier/payment.html', waiting_list=waiting_list)

# API: Lấy chi tiết hóa đơn
@cashier_page.route('/api/bill-detail/<bill_id>', methods=['get'])
def api_bill_detail(bill_id):
    data = dao.get_bill_detail(bill_id)
    print(data)
    if data:
        return jsonify({
            'success': True,
            'id': data['bill'].id,
            'patient_name': data['patient'].fullname,
            'diagnosis': data['bill'].prescrip.diagnosis,
            'medicines': data['medicines'],
            'med_fee': float(data['bill'].medicine_fee),
            'exam_fee': float(data['bill'].medical_fee),
            'total': data['bill'].total
        })
    return jsonify({'success': False})

@cashier_page.route('/api/pay', methods=['POST'])
def api_pay():
    data = request.json
    if dao.pay_bill(data.get('bill_id')):
        return jsonify({'success': True})
    return jsonify({'success': False})

# @cashier_page.route('/api/search/<string:patient>', methods=['POST'])
# def api_search(patient):
#     kw = request.args.get("patient", "")
#
