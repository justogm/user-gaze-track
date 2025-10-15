from werkzeug.security import generate_password_hash, check_password_hash

def is_password_strong(password: str) -> bool:
    return len(password) >= 2

def is_password_valid(password: str, repassword: str) -> bool:
    return password == repassword

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)
