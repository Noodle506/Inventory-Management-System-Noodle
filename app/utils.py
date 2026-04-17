from functools import wraps
from flask import session, redirect, url_for, request

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('auth.login_page', next=request.url))
        return view_func(*args, **kwargs)
    return wrapper