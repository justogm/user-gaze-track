"""
Module docstring TODO: completar
"""

import json
import os
import csv
import io
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    send_from_directory,
    send_file,
)
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from app.models import db, Sujeto, Punto, Medicion, TaskLog


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "instance", "usergazetrack.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

swagger = Swagger(app)


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


@app.route("/guardar-puntos", methods=["POST"])
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
                            fecha:
                                type: string
                                format: date-time
                            gaze:
                                type: object
                                properties:
                                    x:
                                        type: number
                                    y:
                                        type: number
                            mouse:
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
    puntos = data["puntos"]

    for punto in puntos:
        fecha = datetime.strptime(punto["fecha"], "%m/%d/%Y, %I:%M:%S %p")
        punto_gaze = Punto(
            x=punto["gaze"]["x"],
            y=punto["gaze"]["y"],
        )
        db.session.add(punto_gaze)

        punto_mouse = Punto(
            x=punto["mouse"]["x"],
            y=punto["mouse"]["y"],
        )
        db.session.add(punto_mouse)

        nueva_medicion = Medicion(
            fecha=fecha,
            sujeto_id=data["id"],
            punto_gaze=punto_gaze,
            punto_mouse=punto_mouse,
        )
        db.session.add(nueva_medicion)

    db.session.commit()
    return jsonify({"status": "success"})


@app.route("/guardar-tasklogs", methods=["POST"])
def guardar_tasklogs():
    """
    Guarda los registros de tareas (taskLogs) en la base de datos.
    ---
    parameters:
        - name: taskLogs
          in: body
          required: true
          schema:
            type: array
            items:
                type: object
                properties:
                    start_time:
                        type: string
                        format: date-time
                    end_time:
                        type: string
                        format: date-time
                    response:
                        type: string
                    sujeto_id:
                        type: integer
    responses:
        200:
            description: TaskLogs guardados exitosamente.
    """
    data = request.get_json()
    task_logs = data["taskLogs"]
    sujeto_id = data["sujeto_id"]

    for log in task_logs:
        nuevo_log = TaskLog(
            start_time=datetime.strptime(log["startTime"], "%m/%d/%Y, %I:%M:%S %p"),
            end_time=(
                datetime.strptime(log["endTime"], "%m/%d/%Y, %I:%M:%S %p")
                if log["endTime"]
                else None
            ),
            response=log["response"],
            sujeto_id=sujeto_id,
        )
        db.session.add(nuevo_log)

    db.session.commit()
    return jsonify({"status": "success", "message": "TaskLogs guardados exitosamente."})


@app.route("/config")
def config():
    """
    Descarga el archivo de configuración.
    ---
    responses:
        200:
            description: Archivo de configuración.
    """
    return send_from_directory("config", "config.json")


@app.route("/tasks")
def tasks():
    """
    Descarga el archivo de tareas.
    ---
    responses:
        200:
            description: Archivo de tareas.
    """
    return send_from_directory("config", "tasks.json")


@app.route("/descargar-puntos")
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
    sujeto_id = request.args.get("id", type=int)

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        # Obtener las mediciones del sujeto
        mediciones = Medicion.query.filter_by(sujeto_id=sujeto.id).all()

        # Crear el CSV
        si = io.StringIO()
        escritor_csv = csv.writer(si)

        # Escribir encabezados
        escritor_csv.writerow(["fecha", "x_mouse", "y_mouse", "x_gaze", "y_gaze"])

        # Escribir filas
        for medicion in mediciones:
            fila = [
                medicion.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                medicion.punto_mouse.x if medicion.punto_mouse else None,
                medicion.punto_mouse.y if medicion.punto_mouse else None,
                medicion.punto_gaze.x if medicion.punto_gaze else None,
                medicion.punto_gaze.y if medicion.punto_gaze else None,
            ]
            escritor_csv.writerow(fila)

        si.seek(0)

        si_bytes = io.BytesIO(si.getvalue().encode("utf-8"))

        return send_file(
            si_bytes,
            as_attachment=True,
            download_name=f"puntos_sujeto_{sujeto_id}.csv",
            mimetype="text/csv",
        )

    return "Sujeto no encontrado", 404


@app.route("/api/get-sujetos", methods=["GET"])
def api_sujetos():
    """
    Devuelve información sobre los sujetos registrados.
    ---
    responses:
        200:
            description: JSON con la información de los sujetos.
    """
    sujetos = Sujeto.query.all()
    sujetos_info = [
        {
            "id": sujeto.id,
            "nombre": sujeto.nombre,
            "apellido": sujeto.apellido,
            "edad": sujeto.edad,
        }
        for sujeto in sujetos
    ]
    return jsonify(sujetos_info)


@app.route("/api/get-user-points")
def get_user_points():
    sujeto_id = request.args.get("id", type=int)

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        # Obtener las mediciones del sujeto
        mediciones = Medicion.query.filter_by(sujeto_id=sujeto.id).all()

        # Construir una lista de puntos con los datos necesarios
        puntos = []
        for medicion in mediciones:
            punto = {
                "fecha": medicion.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "x_mouse": medicion.punto_mouse.x if medicion.punto_mouse else None,
                "y_mouse": medicion.punto_mouse.y if medicion.punto_mouse else None,
                "x_gaze": medicion.punto_gaze.x if medicion.punto_gaze else None,
                "y_gaze": medicion.punto_gaze.y if medicion.punto_gaze else None,
            }
            puntos.append(punto)

        return jsonify({"sujeto_id": sujeto_id, "puntos": puntos})
    return "Sujeto no encontrado", 404


@app.route("/api/get-user-tasklogs")
def get_user_tasklogs():
    """
    Devuelve los task logs de un sujeto específico.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: ID del sujeto para obtener los task logs.
    responses:
        200:
            description: JSON con los task logs del sujeto.
        404:
            description: Sujeto no encontrado.
    """
    sujeto_id = request.args.get("id", type=int)

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        # Obtener los task logs del sujeto
        task_logs = TaskLog.query.filter_by(sujeto_id=sujeto.id).all()
        task_logs_info = [
            {
                "start_time": log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": (
                    log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None
                ),
                "response": log.response,
            }
            for log in task_logs
        ]
        return jsonify({"sujeto_id": sujeto_id, "task_logs": task_logs_info})
    return "Sujeto no encontrado", 404


@app.route("/descargar-tasks")
def descargar_tasklogs():
    sujeto_id = request.args.get("id", type=int)

    sujeto = Sujeto.query.filter_by(id=sujeto_id).first()

    if sujeto:
        si = io.StringIO()
        escritor_csv = csv.writer(si)

        # Escribir encabezados
        escritor_csv.writerow(["start_time", "end_time", "response"])
        # Obtener los task logs del sujeto
        task_logs = TaskLog.query.filter_by(sujeto_id=sujeto_id).all()
        # Escribir filas
        for log in task_logs:
            fila = [
                log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                log.response,
            ]
            escritor_csv.writerow(fila)
        si.seek(0)
        si_bytes = io.BytesIO(si.getvalue().encode("utf-8"))
        return send_file(
            si_bytes,
            as_attachment=True,
            download_name=f"tasklogs_sujeto_{sujeto_id}.csv",
            mimetype="text/csv",
        )
    else:
        return "Sujeto no encontrado", 404


@app.route("/descargar-todos")
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
    escritor_csv = csv.DictWriter(si, fieldnames=["id", "x", "y"])
    escritor_csv.writeheader()

    if len(all_sujetos) == 0:
        return "No hay sujetos registrados", 404

    for sujeto in all_sujetos:
        puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
        puntos_dict = [punto.__json__() for punto in puntos]

        id_sujeto = int(sujeto.id)

        puntos_np = np.array([[id_sujeto, p["x"], p["y"]] for p in puntos_dict])

        for punto in puntos_np:
            escritor_csv.writerow({"id": punto[0], "x": punto[1], "y": punto[2]})

    si.seek(0)

    si_bytes = io.BytesIO(si.getvalue().encode("utf-8"))
    return send_file(
        si_bytes,
        as_attachment=True,
        download_name="puntos_todos.csv",
        mimetype="text/csv",
    )

@app.route("/visualizacion")
def visualizacion():
    return render_template("visualizacion.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    with open("config/config.json", "r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)
    port_value = config_data.get("port")
    if port_value is None or port_value == "null":  # Check if port is None or "null"
        port = 5001
    else:
        port = int(port_value)  # Ensure port is an integer

    app.run(debug=True, ssl_context=("cert.pem", "key.pem"), port=port)
