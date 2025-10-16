"""
Module docstring TODO: completar
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)
from flasgger import Swagger
from db import DatabaseConfig, DatabaseManager, db, Subject, Measurement
from api.routes import api_bp
from state import ConfigManager
from repositories import SubjectRepository, MeasurementRepository


basedir = os.path.abspath(os.path.dirname(__file__))

config_manager = ConfigManager()
config_manager.load_config()

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

db_config = DatabaseConfig(basedir)
db_config.configure_app(app)

db_manager = DatabaseManager(app)

subject_repository = SubjectRepository()
measurement_repository = MeasurementRepository()

app.register_blueprint(api_bp)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "User Gaze Track API",
        "description": "API for user gaze tracking and data management",
        "version": "1.0.0",
        "contact": {
            "name": "User Gaze Track Team",
        },
    },
    "host": "localhost:5001",
    "basePath": "/",
    "schemes": ["https", "http"],
    "securityDefinitions": {},
    "tags": [
        {"name": "web", "description": "Web interface routes"},
        {"name": "api", "description": "REST API endpoints"},
    ],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page that allows registration of a new subject for gaze measurement.
    ---
    parameters:
      - name: nombre
        in: formData
        type: string
        required: true
        description: Subject's name.
      - name: apellido
        in: formData
        type: string
        required: true
        description: Subject's surname.
      - name: edad
        in: formData
        type: integer
        required: true
        description: Subject's age.
    responses:
      200:
        description: Home page or redirect to tracking page.
    """
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        edad = request.form["edad"]

        subject = subject_repository.create_subject(
            name=nombre,
            surname=apellido,
            age=edad
        )
        subject_repository.commit()

        return redirect(url_for("embed", id=subject.id))
    return render_template("index.html")


@app.route("/gaze-tracking")
def embed():
    """
    Shows the eye tracking page for the user with the ID passed as parameter.
    ---
    parameters:
      - name: id
        in: query
        type: integer
        required: true
        description: Subject ID for eye tracking.
    responses:
      200:
        description: Eye tracking page.
    """
    return render_template("embed.html", id=request.args.get("id"))


@app.route("/fin-medicion")
def fin_medicion():
    """
    Shows the measurement completion page.
    ---
    responses:
        200:
            description: Measurement completion page.
    """
    return render_template("fin.html")


@app.route("/sujetos")
def sujetos():
    """
    Shows the list of registered subjects in the database.
    ---
    responses:
        200:
            description: Page with the list of registered subjects.
    """
    subjects_db = subject_repository.get_all_subjects()
    return render_template("sujetos.html", sujetos=subjects_db)


@app.route("/resultados")
def resultados():
    """
    Shows the results of registered points for a specific subject and allows download.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to show results.
    responses:
        200:
            description: Page with the registered points results.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    subject = subject_repository.get_subject_by_id(subject_id)

    if subject:
        measurements = measurement_repository.get_measurements_by_subject(subject_id=subject_id)

        points = []
        for measurement in measurements:
            if measurement.mouse_point:
                points.append(
                    {"x": measurement.mouse_point.x, "y": measurement.mouse_point.y}
                )
            if measurement.gaze_point:
                points.append({"x": measurement.gaze_point.x, "y": measurement.gaze_point.y})

        return render_template("resultados.html", sujeto=subject, puntos=points)

    return "Subject not found", 404


@app.route("/visualizacion")
def visualizacion():
    return render_template("visualizacion.html")


if __name__ == "__main__":
    db_manager.create_all()

    config_manager.print_config()
    
    port = config_manager.get_port(default=5001)

    app.run(debug=True, ssl_context=("cert.pem", "key.pem"), port=port)
