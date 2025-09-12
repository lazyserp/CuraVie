# decorators.py

# 1. Imports
# Imports a helper function 'wraps' that makes our decorator behave like the original function it's wrapping.
from functools import wraps
# Imports 'flash' to show messages to users and 'abort' to stop a request with an error page (like '403 Forbidden').
from flask import flash, abort
# Imports 'current_user' from the Flask-Login library, which represents the user currently logged into the session.
from flask_login import current_user
# Imports our custom 'UserRoleEnum', which likely defines different user roles like ADMIN, USER, etc.
from models import UserRoleEnum

# 2. The Decorator "Factory"
# This is a function that creates and returns a decorator. We pass it the 'role' we want to check for.
def role_required(role):
    # 3. The Actual Decorator
    # This is the actual decorator. It takes a function 'f' (like a Flask route) as its argument.
    def decorator(f):
        # 4. The Wrapper Function (The Guard's Logic)
        # This copies the name and other info from the original function 'f' to our new 'decorated_function'.
        @wraps(f)
        # This is the new function that runs instead of the original one. It will contain our security checks.
        def decorated_function(*args, **kwargs):
            # Check 1: Is the user logged in at all?
            # 'is_authenticated' is True if the user is logged in, so 'not' checks if they are NOT logged in.
            if not current_user.is_authenticated:
                # If they aren't logged in, stop everything and show a "403 Forbidden" error page.
                abort(403) # Not allowed, period.
            
            # Check 2: Does the user have the specific role required?
            # Compares the logged-in user's role to the 'role' this decorator was created to check for.
            if current_user.role != role:
                # If the roles don't match, prepare an error message to show the user on the next page.
                flash("You do not have permission to access this page.", "error")
                # Stop everything and show a "403 Forbidden" error page because they don't have the right permissions.
                abort(403) # Forbidden!
            
            # If both checks pass, run the original view function.
            # Call the original function 'f' that this decorator was protecting.
            return f(*args, **kwargs)
        # The 'decorator' returns the newly created wrapper function.
        return decorated_function
    # The 'role_required' factory returns the 'decorator' itself.
    return decorator

# 5. Creating Simple, Reusable Decorators
# We create a specific decorator named 'admin_required' by calling our factory with the ADMIN role.
admin_required = role_required(UserRoleEnum.ADMIN)
# We create another specific decorator for health officials. Now we can just use '@health_official_required'.
health_official_required = role_required(UserRoleEnum.HEALTH_OFFICIAL)