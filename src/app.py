"""
Module docstring TODO: completar
"""

import json
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from app.models import db, Sujeto, Medicion
from api.routes import api_bp


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "../instance", "usergazetrack.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

# Register API blueprint
app.register_blueprint(api_bp)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "User Gaze Track API",
        "description": "API para el seguimiento de la mirada del usuario y gestión de datos",
        "version": "1.0.0",
        "contact": {
            "name": "User Gaze Track Team",
        }
    },
    "host": "localhost:5001",
    "basePath": "/",
    "schemes": ["https", "http"],
    "securityDefinitions": {},
    "tags": [
        {
            "name": "web",
            "description": "Rutas de la interfaz web"
        },
        {
            "name": "api",
            "description": "Endpoints de la API REST"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)


@app.route("/", methods=["GET", "POST"])
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
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]

        sujeto = Sujeto(nombre=nombre, apellido=apellido, edad=edad)
        db.session.add(sujeto)
        db.session.commit()

        return redirect(url_for("embed", id=sujeto.id))
    return render_template("index.html")


@app.route("/gaze-tracking")
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
    return render_template("embed.html", id=request.args.get("id"))


@app.route("/fin-medicion")
def fin_medicion():
    """
    Muestra la página de finalización de la medición.
    ---
    responses:
        200:
            description: Página de finalización de la medición.
    """
    return render_template("fin.html")


@app.route("/sujetos")
def sujetos():
    """
    Muestra la lista de sujetos registrados en la base de datos.
    ---
    responses:
        200:
            description: Página con la lista de sujetos registrados.
    """
    sujetos_db = Sujeto.query.all()
    return render_template("sujetos.html", sujetos=sujetos_db)


@app.route("/resultados")
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
    sujeto_id = request.args.get("id", type=int)

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        # Obtener las mediciones del sujeto
        mediciones = Medicion.query.filter_by(sujeto_id=sujeto.id).all()

        # Construir una lista de puntos con solo x e y
        puntos = []
        for medicion in mediciones:
            if medicion.punto_mouse:
                puntos.append(
                    {"x": medicion.punto_mouse.x, "y": medicion.punto_mouse.y}
                )
            if medicion.punto_gaze:
                puntos.append({"x": medicion.punto_gaze.x, "y": medicion.punto_gaze.y})

        return render_template("resultados.html", sujeto=sujeto, puntos=puntos)

    return "Sujeto no encontrado", 404


@app.route("/visualizacion")
def visualizacion():
    return render_template("visualizacion.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    with open("src/config/config.json", "r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)
    port_value = config_data.get("port")
    if port_value is None or port_value == "null":  # Check if port is None or "null"
        port = 5001
    else:
        port = int(port_value)  # Ensure port is an integer

    app.run(debug=True, ssl_context=("cert.pem", "key.pem"), port=port)
