"""
Module docstring TODO: completar
"""
import os
import csv
import io
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from app.models import db, Sujeto, Punto



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
    Página principal que permite el registro de un nuevo sujeto para la medición de su mirada.
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
    """
    Muestra la lista de sujetos registrados en la base de datos.
    ---
    responses:
        200:
            description: Página con la lista de sujetos registrados.
    """
    sujetos_db = Sujeto.query.all()
    return render_template('sujetos.html', sujetos=sujetos_db)

@app.route('/resultados')
def resultados():
    """
    Muestra los resultados de los puntos registrados para un sujeto en particular y \
        permite su descarga.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: ID del sujeto para mostrar resultados.
    responses:
        200:
            description: Página con los resultados de los puntos registrados.
        404:
            description: Sujeto no encontrado.
    """
    sujeto_id = request.args.get('id')

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
        puntos_dict = [punto.__json__() for punto in puntos]
        return render_template('resultados.html', sujeto=sujeto, puntos=puntos_dict)

    return "Sujeto no encontrado", 404

@app.route('/guardar-puntos', methods=['POST'])
def guardar_puntos():
    """
    Guarda los puntos registrados en la base de datos.
    ---
    parameters:
        - name: puntos
          in: body
          required: true
          schema:
            type: object
            properties:
                id:
                    type: integer
                puntos:
                    type: array
                    items:
                        type: object
                        properties:
                            x:
                                type: number
                            y:
                                type: number
    responses:
        200:
            description: status success
    """
    data = request.get_json()
    puntos = data['puntos']

    for punto in puntos:
        nuevo_punto = Punto(x=punto['x'], y=punto['y'], sujeto_id=data['id'])
        db.session.add(nuevo_punto)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/config')
def config():
    """
    Descarga el archivo de configuración.
    ---
    responses:
        200:
            description: Archivo de configuración.
    """
    return send_from_directory('config', 'config.json')


@app.route('/descargar-puntos')
def descargar_puntos():
    """
    Descarga los puntos registrados para un sujeto en particular.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: ID del sujeto para descargar los puntos.
    responses:
        200:
            description: Archivo CSV con los puntos registrados.
        404:
            description: Sujeto no encontrado.
    """
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

        si_bytes = io.BytesIO(si.getvalue().encode('utf-8')) \
                                            #Tiene que estar en este formato para send_file

        return send_file(
            si_bytes,
            as_attachment=True,
            download_name=f"puntos_sujeto_{sujeto_id}.csv",
            mimetype='text/csv'
        )

    return "Sujeto no encontrado", 404

@app.route('/descargar-todos')
def descargar_todos():
    """
    Descarga los puntos registrados para todos los sujetos en formato csv.
    ---
    responses:
        200:
            description: Archivo CSV con los puntos registrados para todos los sujetos.
        404:
            description: No hay sujetos registrados.
    """
    all_sujetos = Sujeto.query.all()

    si = io.StringIO()
    escritor_csv = csv.DictWriter(si, fieldnames=['id', 'x', 'y'])
    escritor_csv.writeheader()

    if len(sujetos) == 0:
        return "No hay sujetos registrados", 404

    for sujeto in all_sujetos:
        puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
        puntos_dict = [punto.__json__() for punto in puntos]

        id_sujeto = int(sujeto.id)

        puntos_np = np.array([[id_sujeto, p['x'], p['y']] for p in puntos_dict])

        for punto in puntos_np:
            escritor_csv.writerow({'id': punto[0], 'x': punto[1], 'y': punto[2]})


    si.seek(0)

    si_bytes = io.BytesIO(si.getvalue().encode('utf-8'))
    return send_file(
        si_bytes,
        as_attachment=True,
        download_name="puntos_todos.csv",
        mimetype='text/csv'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
