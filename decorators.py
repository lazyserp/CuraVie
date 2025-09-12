from flask_login import current_user
from flask import request

def require_role(allowed_roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user_role = request.args.get("role")
            if user_role in allowed_roles:
                return func(*args, **kwargs)
            else:
                return f" Access Denied for role: {user_role}", 403
        return wrapper
    return decorator
