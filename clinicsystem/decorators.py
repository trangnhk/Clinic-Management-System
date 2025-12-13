from functools import wraps
from flask import redirect
from flask_login import current_user


ROLE_REDIRECT = {
    "Nurse": "/nurse",
    "Doctor": "/doctor",
    "Cashier": "/cashier",
    "Administrator": "/admin"
}

def anonymous_required(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(ROLE_REDIRECT.get(current_user.__class__.__name__, "/"))
        return f(*args, **kwargs)
    return decorated_func