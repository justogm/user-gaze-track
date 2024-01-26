from flask import Flask, render_template, request, redirect, url_for
from app.models import db, Sujeto, Trayectoria, Punto
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'usergazetrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']
        return redirect(url_for('embed', nombre=nombre, apellido=apellido, edad=edad))
    return render_template('index.html')

@app.route('/gaze-tracking')
def embed():
    nombre = request.args.get('nombre')
    apellido = request.args.get('apellido')
    edad = request.args.get('edad')

    trayectoria = Trayectoria()
    db.session.add(trayectoria)
    sujeto = Sujeto(nombre=nombre, apellido=apellido, edad=edad, trayectoria_rel=trayectoria)
    db.session.add(sujeto)
    db.session.commit()

    return render_template('embed.html', nombre=nombre, apellido=apellido, edad=edad)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
