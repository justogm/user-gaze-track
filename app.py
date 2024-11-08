from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file
from app.models import db, Sujeto, Punto
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import os
import csv
import io

basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'instance', 'usergazetrack.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

swagger = Swagger(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Página principal que permite el registro de un nuevo sujeto para la medición de su \
        mirada.
    ---
    parameters:
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nombre del sujeto.
      - name: apellido
        in: formData
        type: string
        required: true
        description: Apellido del sujeto.
      - name: edad
        in: formData
        type: integer
        required: true
        description: Edad del sujeto.
    responses:
      200:
        description: Página de inicio o redirección a la página de seguimiento.
    """
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
    """
    Muestra la página de seguimiento ocular para el usuario con el id que se pasa como parámetro.
    ---
    parameters:
      - name: id
        in: query
        type: integer
        required: true
        description: ID del sujeto para seguimiento ocular.
    responses:
      200:
        description: Página de seguimiento ocular.
    """
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
        puntos_dict = [punto.__json__() for punto in puntos]
        return render_template('resultados.html', sujeto=sujeto, puntos=puntos_dict)

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

@app.route('/config')
def config():
    return send_from_directory('config', 'config.json')


@app.route('/descargar-puntos')
def descargar_puntos():
    sujeto_id = request.args.get('id')

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
        puntos_dict = [punto.__json__() for punto in puntos]

        si = io.StringIO()
        escritor_csv = csv.DictWriter(si, fieldnames=puntos_dict[0].keys())
        escritor_csv.writeheader()  # escribe los encabezados
        escritor_csv.writerows(puntos_dict)  # escribe los datos

        si.seek(0)

        si_bytes = io.BytesIO(si.getvalue().encode('utf-8')) #Tiene que estar en este formato para send_file

        return send_file(
            si_bytes,
            as_attachment=True,
            download_name=f"puntos_sujeto_{sujeto_id}.csv",
            mimetype='text/csv'
        )

    return "Sujeto no encontrado", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
