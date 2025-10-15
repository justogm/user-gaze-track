from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from modules.auth.controller import register_user, authenticate_user, verify_user
from modules.auth.controller import send_password_recovery_email, is_a_valid_password
from modules.auth.controller import reset_password_on_user, verify_user_pw_reset
from modules.auth.decorators import login_required
from modules.auth.oauth import google, github


auth_bp = Blueprint('auth', __name__)

_LOGIN_REDIRECT_ENDPOINT = 'auth.auth_dashboard'  # Valor por defecto

def set_login_redirect(endpoint):
    global _LOGIN_REDIRECT_ENDPOINT
    _LOGIN_REDIRECT_ENDPOINT = endpoint

@auth_bp.route('/inicio')
def inicio():
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        repassword = request.form['repassword']
        is_valid, message = is_a_valid_password(password, repassword)
        if not is_valid:
            flash(message, "danger")
            return redirect(url_for('auth.register'))
        else:
            try:
                register_user(email, password) # TODO: register_user retorna un valor?
                flash("Revisa tu correo para verificar tu cuenta.", "success")
                return redirect(url_for('auth.login'))
            except ValueError as e:
                flash(str(e), "danger")
    return render_template('register.html')

@auth_bp.route('/pwrecovery', methods=['GET', 'POST'])
def pw_recovery():
    if request.method == 'POST':
        email = request.form['email']
        try:
            send_password_recovery_email(email)
            # Aquí deberías implementar la lógica para enviar un correo de recuperación
            flash("Si el correo existe, se ha enviado un enlace de recuperación.", "info")
            return render_template('pwrecovery.html')
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for('auth.login'))
    else:
        return render_template('pwrecovery.html')

@auth_bp.route('/pwreset', methods=['GET', 'POST'])
def pw_reset():
    if request.method == 'POST':
        if 0 < session['pw_reset_number_access_to_pw_reset']:  # Por si se trata de reentrar a este endpoint para hackear cambio de contraseña
            flash("Restablecimiento de contraseña expirado.", "danger")
            return redirect(url_for('auth.login'))
        session['pw_reset_number_access_to_pw_reset'] += 1 # Permitido un solo acceso a este endpoint desde el inicio del proceso de recuperación
        email = session['pw_reset_email']
        password = request.form['password']
        repassword = request.form['repassword']
        is_valid, message = is_a_valid_password(password, repassword)
        if not is_valid:
            flash(message, "danger")
            return redirect(url_for('auth.login'))    
        else:
            try:
                reset_password_on_user(email, password)
                flash("Contraseña actualizada correctamente.", "success")
                return redirect(url_for('auth.login'))
            except ValueError as e:
                flash(str(e), "danger")
        return render_template('login.html')
    else:
        return render_template('pwreset.html')

@auth_bp.route('/reset_password/<token>')
def pw_reset_token(token):
    email = verify_user_pw_reset(token)
    if email is not None:
        session['pw_reset_email'] = email
        session['pw_reset_number_access_to_pw_reset'] = 0
        flash("Correo verificado, ya puedes definir tu nueva contraseña.", "success")
        return redirect(url_for('auth.pw_reset')) # NOTE: 307 para que mantenga el método POST
    else:
        flash("El enlace es inválido o expiró.", "danger")
        return redirect(url_for('auth.login'))


@auth_bp.route('/verify/<token>')
def verify(token):
    if verify_user(token):
        flash("Correo verificado, ya podés iniciar sesión.", "success")
        return redirect(url_for('auth.login'))
    else:
        flash("El enlace es inválido o expiró.", "danger")
        return redirect(url_for('auth.register'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            if authenticate_user(email, password):
                session['email'] = email
                flash("Inicio de sesión exitoso.", "success")
                return redirect(url_for(_LOGIN_REDIRECT_ENDPOINT))  # Usa la variable global
            else:
                flash("Correo o contraseña incorrectos.", "danger")
        except ValueError as e:
            flash(str(e), "warning")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('email', None)
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/auth-dashboard')
@login_required
def auth_dashboard():
    return render_template('auth_dashboard.html')

@auth_bp.route("/google")
def google_login():
    flash("Inicio de sesión con Google en desarrollo", "info")
    # if not google.authorized:
    #     return redirect(url_for("auth.google_login"))
    # resp = google.get("/oauth2/v2/userinfo")
    # user_info = resp.json()
    # create_or_get_user_oauth(email=user_info["email"], name=user_info.get("name"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/github")
def github_login():
    flash("Inicio de sesión con GitHub en desarrollo", "info")

    # if not github.authorized:
    #     return redirect(url_for("auth.github_login"))
    # resp = github.get("/user")
    # user_info = resp.json()
    # email = user_info.get("email")
    # if not email:  # A veces GitHub no da el email, hay que pedirlo aparte
    #     emails_resp = github.get("/user/emails")
    #     email = emails_resp.json()[0]["email"]
    # create_or_get_user_oauth(email=email, name=user_info.get("login"))
    return redirect(url_for("auth.login"))


if __name__ == '__main__':
    print(url_for("login"))