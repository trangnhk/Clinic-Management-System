# Clinic Management System

A role-based **Clinic Management System** built with **Python Flask**, supporting full workflows for Admins, Doctors, Nurses, Cashiers, and Patients within a single web application.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [User Roles](#user-roles)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This system digitizes the end-to-end workflow of a medical clinic — from patient registration and appointment booking, to clinical examination, prescription management, and payment processing. Each user role has a dedicated module built with Flask Blueprints for clean separation of concerns.

---

## Features

### 1. Authentication
- Login and registration for all roles
- Role-based route protection via custom decorators (`decorators.py`)

### 2. Admin
- View clinic statistics and charts via dashboard (`stats.html`, `drawChart.js`)
- Manage system-wide configurations

### 3. Doctor
- View patient waiting list
- Perform clinical examinations
- Write and manage prescriptions (medicines, dosage)
- Check patient medical history and allergy information
- Search medicines by name

### 4. Nurse
- Register and add new patients (`addPatient.html`)
- Manage daily examination list

### 5. Cashier
- Process patient payments after consultation (`payment.html`, `pay.js`)
- Generate appointment tickets (`appointment_ticket.html`)

### 6. Patient
- Book clinic appointments (`appointment.html`)
- View personal appointment history

---

## Tech Stack

| Layer          | Technology                              |
|----------------|------------------------------------------|
| Language       | Python 3.12                              |
| Web Framework  | Flask (Blueprint architecture)           |
| Templating     | Jinja2 (HTML templates)                  |
| Frontend       | HTML, CSS, JavaScript (Vanilla)          |
| Database ORM   | SQLAlchemy (via `models.py` + `dao.py`)  |
| Database       | MySQL / SQLite                           |
| Config/Data    | JSON (menu bars, fake data)              |

---

## Project Structure

```
Clinic-Management-System/
├── clinicsystem/
│   ├── __init__.py              # App factory
│   ├── models.py                # SQLAlchemy database models
│   ├── dao.py                   # Data Access Object layer
│   ├── decorators.py            # Role-based access decorators
│   ├── index.py                 # Main routes (login, register, home)
│   ├── fake_data.py             # Script to seed sample data
│   │
│   ├── admin/                   # Admin Blueprint
│   │   └── routes.py
│   ├── doctor/                  # Doctor Blueprint
│   │   └── routes.py
│   ├── nurse/                   # Nurse Blueprint
│   │   └── routes.py
│   ├── cashier/                 # Cashier Blueprint
│   │   └── routes.py
│   │
│   ├── static/
│   │   ├── css/styles.css
│   │   ├── js/                  # Feature-specific JS files
│   │   └── logo/
│   │
│   ├── templates/               # Jinja2 HTML templates per role
│   │   ├── admin/
│   │   ├── doctor/
│   │   ├── nurse/
│   │   ├── cashier/
│   │   └── patient/
│   │
│   ├── data/                    # JSON config files (menu bars, etc.)
│   └── run-flask.sh             # Shell script to start the server
│
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- pip
- MySQL (or SQLite for local dev)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/trangnhk/Clinic-Management-System.git
   cd Clinic-Management-System
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your database**

   Update the database URI in `clinicsystem/__init__.py` or via environment variables:
   ```python
   SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@localhost/clinic_db"
   ```

5. **Seed sample data (optional)**
   ```bash
   python clinicsystem/fake_data.py
   ```

6. **Run the application**
   ```bash
   bash clinicsystem/run-flask.sh
   # or manually:
   flask --app clinicsystem run --debug
   ```

7. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

---

## User Roles

| Role      | Key Capabilities                                                             |
|-----------|------------------------------------------------------------------------------|
| **Admin**    | View clinic statistics, manage system settings                            |
| **Doctor**   | Examine patients, write prescriptions, view history & allergies           |
| **Nurse**    | Register patients, manage examination list                                |
| **Cashier**  | Process payments, generate appointment tickets                            |
| **Patient**  | Book appointments, view appointment history                               |

---

## Contributing

1. Fork the repository
2. Create a new feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add: your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).

> Any modified version of this project that is used to provide a network service must also be released under the AGPL-3.0 license with its full source code made publicly available.

---

## Author

**trangnhk**
- GitHub: [@trangnhk](https://github.com/trangnhk)

---

> *Developed as a Software Engineering course project.*
