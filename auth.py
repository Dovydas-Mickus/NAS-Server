from flask import request, session, redirect, url_for
from argon2 import PasswordHasher
from database import get_user_by_email


ph = PasswordHasher()

def login_attempt(email, password):
    # Retrieve the user by username from the database
    user = get_user_by_email(email)
    
    if user and ph.verify(user['password_hash'], password):
        # Password matches, login successful
        return user
    else:
        # Incorrect username or password
        return None
    
def check_session(session, request):
    """Check if user is logged in by checking the session."""
    if not check_ip(request):
        return False

    if 'user_id' not in session:
        # If not logged in, redirect to the login page
        return False
    return True  # If logged in, return None or any success response


def check_ip(request):
    client_ip = request.remote_addr
    
    # Check if the client IP is a local IP (local network)
    if client_ip.startswith('192.168.') or client_ip == '127.0.0.1':
        return True
    else:
        print("User is not local!")
        return False
            