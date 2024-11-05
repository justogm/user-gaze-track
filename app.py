from flask import Flask, render_template, request, redirect, url_for, jsonify
from app.models import db, Sujeto, Punto
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'instance', 'usergazetrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        edad = request.form['edad']

        sujeto = Sujeto(nombre=nombre, apellido=apellido, edad=edad)
        db.session.add(sujeto)
        db.session.commit()

        return redirect(url_for('embed', id=sujeto.id))
    return render_template('index.html')

@app.route('/gaze-tracking')
def embed():
    return render_template('embed.html', id=request.args.get('id'))


@app.route('/sujetos')
def sujetos():
    sujetos_db = Sujeto.query.all()
    return render_template('sujetos.html', sujetos=sujetos_db)

@app.route('/resultados')
def resultados():
    sujeto_id = request.args.get('id')

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
        return render_template('resultados.html', sujeto=sujeto, puntos=puntos)

    return "Sujeto no encontrado", 404

@app.route('/guardar-puntos', methods=['POST'])
def guardar_puntos():
    data = request.get_json()
    puntos = data['puntos']

    for punto in puntos:
        nuevo_punto = Punto(x=punto['x'], y=punto['y'], sujeto_id=data['id'])
        db.session.add(nuevo_punto)
    db.session.commit()
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
