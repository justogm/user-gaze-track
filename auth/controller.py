
from modules.auth.security import hash_password, verify_password,is_password_strong, is_password_valid
from modules.auth.email_verification import generate_confirmation_token, confirm_token, send_email

# Simulación base de datos simple
users_db = {}
users_db["javier.diaz@uner.edu.ar"]={'password': hash_password("123"), 'verified': True}
used_pw_reset_tokens = set()

def register_user(email, password):
    if email in users_db:
        raise ValueError("Usuario ya existe")
    pwd_hash = hash_password(password)
    users_db[email] = {'password': pwd_hash, 'verified': False}
    token = generate_confirmation_token(email)
    verify_url = f"http://localhost:5000/verify/{token}"
    send_email(email, "Confirma tu cuenta", f"Por favor confirma tu correo haciendo clic aquí: {verify_url}")
    return True

def reset_password_on_user(email, password):
    if email not in users_db:
        raise ValueError("Usuario no existe")
    pwd_hash = hash_password(password)
    users_db[email]['password'] = pwd_hash # NOTE: se mantiene el estado de verificación
    return True

def verify_user(token):
    email = confirm_token(token)
    if not email or email not in users_db:
        return False
    users_db[email]['verified'] = True
    return True

def verify_user_pw_reset(token):
    """
    Verifica si el token de recuperación es válido y no ha expirado. 
    Devuelve el email si es válido, None si no lo es.
    """
    email = confirm_token(token)

    # --------------------------------------------------------------------
    # Prevenir reutilización de tokens para restablecimiento de contraseña
    # --------------------------------------------------------------------
    # Token ya utilizado e email válido (implica: token reutilizado)
    if token in used_pw_reset_tokens and email in users_db: 
        return None
    used_pw_reset_tokens.add(token)
    
    # Token ya utilizado pero email no válido (implica: token expirado, no debería estar más en used_pw_reset_tokens)
    if token in used_pw_reset_tokens and email is None: 
        used_pw_reset_tokens.remove(token)
    
    # Email no válido o no existe en la "base de datos"
    if not email or email not in users_db:
        return None
    return email

def authenticate_user(email, password):
    user = users_db.get(email)
    if not user:
        return False
    if not user['verified']:
        raise ValueError("El correo no está verificado")
    if verify_password(password, user['password']):
        return True
    return False

def create_or_get_user_oauth(email, name=None, provider=None):
    """
    Si el usuario no existe, lo crea marcado como verificado (porque viene de OAuth).
    Devuelve el dict del usuario.
    """
    user = users_db.get(email)
    if user:
        return user
    users_db[email] = {'password': None, 'verified': True, 'name': name, 'oauth': provider}
    return users_db[email]

def send_password_recovery_email(email):
    if email not in users_db:
        raise ValueError("No existe usuario con ese correo")
    else:
        token = generate_confirmation_token(email)
        recovery_url = f"http://localhost:5000/reset_password/{token}"
        send_email(email, "Recuperación de contraseña", f"Para restablecer tu contraseña, haz clic aquí: {recovery_url}")
        return True

def is_a_valid_password(password: str, repassword:str) -> tuple[bool,str]:
    """
    Verifica si la contraseña cumple con la regla y si son contraseñas son iguales .
    """
    message = "La contraseña es válida."
    result = True
    if not is_password_strong(password):
        message = "La contraseña debe tener al menos 8 caracteres." # TODO: Este mensaje debe coincidir con lo que realmente verifica la función is_password_strong
        result = False
    elif not is_password_valid(password, repassword):
        message = "Las contraseñas no coinciden."
        result = False

    return result, message