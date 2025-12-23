from datetime import datetime, date

from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound

from clinicsystem import dao

admin_page = Blueprint(
    'admin',
    __name__,
    url_prefix="/admin"
)

# /admin
@admin_page.route('/')
@login_required
def admin_home_info():
    try:
        return render_template('home_info.html', user=current_user, role="admin")
    except TemplateNotFound:
        abort(404)

@admin_page.route('/stats', methods=['get'])
@login_required
def admin_stats():
    # Lấy danh sách những năm có dữ liệu
    available_years = dao.get_available_years()
    default_year = available_years[0] if available_years else datetime.now().year

    # Lấy tháng năm hiện tại làm mặc định
    month = request.args.get('month', 12, type=int)
    year = request.args.get('year', default_year, type=int)
    report_type = request.args.get('type', 'overview') # mặc định xem overview


    if report_type == 'overview':
        stats_data = dao.overview_report(month, year)
        return render_template(
            'admin/stats.html',
            stats=stats_data,
            report_type=report_type,
            month=month,
            year=year,
            available_years=available_years
        )


    elif report_type == 'revenue':
        stats_data = dao.revenue_report(month, year)
        print(stats_data)
        return render_template(
            'admin/stats.html',
            table_data=stats_data["table"],
            chart_data=stats_data["chart"],
            report_type=report_type,
            month=month,
            year=year,
            available_years=available_years
        )

    else:  # medicine
        stats_data = dao.medicine_report(month, year)
        print(stats_data)
        return render_template(
            'admin/stats.html',
            stats=stats_data,
            report_type=report_type,
            month=month,
            year=year,
            available_years=available_years
        )



