from functools import wraps
from flask_login import current_user
from flask import abort

def require_role(allowed_roles: list):
    """
    The security guard which checks role of the current user.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Check if the user is authenticated at all.
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized

            # 2. Get the user's role value from the trusted session object.
            user_role_value = current_user.role.value

            # 3. If their role is not in the list of allowed roles, deny access.
            if user_role_value not in allowed_roles:
                abort(403)  # Forbidden
            
            return func(*args, **kwargs)
        return wrapper
    return decorator