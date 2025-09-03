"""
API routes for the user gaze tracking application.
"""

from flask import Blueprint, request, jsonify, send_file, send_from_directory
from .services import SujetoService, MedicionService, TaskLogService, ExportService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route("/get-sujetos", methods=["GET"])
def api_sujetos():
    """
    Devuelve información sobre los sujetos registrados.
    ---
    responses:
        200:
            description: JSON con la información de los sujetos.
    """
    sujetos_info = SujetoService.get_all_sujetos()
    return jsonify(sujetos_info)


@api_bp.route("/get-user-points")
def get_user_points():
    """
    Devuelve los puntos de gaze y mouse de un sujeto específico.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: ID del sujeto para obtener los puntos.
    responses:
        200:
            description: JSON con los puntos del sujeto.
        404:
            description: Sujeto no encontrado.
    """
    sujeto_id = request.args.get("id", type=int)
    
    result = MedicionService.get_user_points(sujeto_id)
    if result:
        return jsonify(result)
    return "Sujeto no encontrado", 404


@api_bp.route("/get-user-tasklogs")
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
    
    result = TaskLogService.get_user_tasklogs(sujeto_id)
    if result:
        return jsonify(result)
    return "Sujeto no encontrado", 404


@api_bp.route("/guardar-puntos", methods=["POST"])
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
    result = MedicionService.save_puntos(data)
    return jsonify(result)


@api_bp.route("/guardar-tasklogs", methods=["POST"])
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
    result = TaskLogService.save_tasklogs(data)
    return jsonify(result)


@api_bp.route("/config")
def config():
    """
    Descarga el archivo de configuración.
    ---
    responses:
        200:
            description: Archivo de configuración.
    """
    return send_from_directory("config", "config.json")


@api_bp.route("/tasks")
def tasks():
    """
    Descarga el archivo de tareas.
    ---
    responses:
        200:
            description: Archivo de tareas.
    """
    return send_from_directory("config", "tasks.json")


@api_bp.route("/descargar-puntos")
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
    
    csv_data = ExportService.export_puntos_csv(sujeto_id)
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name=f"puntos_sujeto_{sujeto_id}.csv",
            mimetype="text/csv",
        )
    
    return "Sujeto no encontrado", 404


@api_bp.route("/descargar-tasklogs")
def descargar_tasklogs():
    """
    Descarga los task logs registrados para un sujeto en particular.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: ID del sujeto para descargar los task logs.
    responses:
        200:
            description: Archivo CSV con los task logs registrados.
        404:
            description: Sujeto no encontrado.
    """
    sujeto_id = request.args.get("id", type=int)
    
    csv_data = ExportService.export_tasklogs_csv(sujeto_id)
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name=f"tasklogs_sujeto_{sujeto_id}.csv",
            mimetype="text/csv",
        )
    else:
        return "Sujeto no encontrado", 404


@api_bp.route("/descargar-todos")
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
    csv_data = ExportService.export_all_puntos_csv()
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name="puntos_todos.csv",
            mimetype="text/csv",
        )
    else:
        return "No hay sujetos registrados", 404
