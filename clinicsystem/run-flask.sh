#!/bin/bash

echo "--- Cài thư viện ---"
pip install -r requirements.txt

echo "--- Thiết lập Flask ---"
export FLASK_APP=clinicsystem
export FLASK_ENV=development

echo "--- Tạo database & dữ liệu ---"
flask shell << EOF
from clinicsystem import app, db, register_blueprints
from clinicsystem import models

register_blueprints()

with app.app_context():
    db.create_all()

print(">>> Database created")
EOF

echo "--- Tạo account user --"
python clinicsystem/dao.py

echo "--- Tạo fake date ---"
python clinicsystem/fake_data.py

echo "--- Chạy ứng dụng ---"
python -m flask run clinicsystem/index.py
