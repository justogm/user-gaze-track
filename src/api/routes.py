"""
API routes for the user gaze tracking application.
"""

from flask import Blueprint, request, jsonify, send_file, send_from_directory
from .services import SubjectService, MeasurementService, TaskLogService, ExportService

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/get-subjects", methods=["GET"])
def api_subjects():
    """
    Returns information about registered subjects.
    ---
    responses:
        200:
            description: JSON with subjects information.
    """
    subjects_info = SubjectService.get_all_subjects()
    return jsonify(subjects_info)


@api_bp.route("/get-user-points")
def get_user_points():
    """
    Returns gaze and mouse points for a specific subject.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to get the points.
    responses:
        200:
            description: JSON with subject points.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    result = MeasurementService.get_user_points(subject_id)
    if result:
        return jsonify(result)
    return "Subject not found", 404


@api_bp.route("/get-user-tasklogs")
def get_user_tasklogs():
    """
    Returns task logs for a specific subject.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to get the task logs.
    responses:
        200:
            description: JSON with subject task logs.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    result = TaskLogService.get_user_tasklogs(subject_id)
    if result:
        return jsonify(result)
    return "Subject not found", 404


@api_bp.route("/save-points", methods=["POST"])
def save_points():
    """
    Saves recorded points to the database.
    ---
    parameters:
        - name: points
          in: body
          required: true
          schema:
            type: object
            properties:
                id:
                    type: integer
                points:
                    type: array
                    items:
                        type: object
                        properties:
                            date:
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
    result = MeasurementService.save_points(data)
    return jsonify(result)


@api_bp.route("/save-tasklogs", methods=["POST"])
def save_tasklogs():
    """
    Saves task logs (taskLogs) to the database.
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
                    subject_id:
                        type: integer
    responses:
        200:
            description: TaskLogs saved successfully.
    """
    data = request.get_json()
    result = TaskLogService.save_tasklogs(data)
    return jsonify(result)


@api_bp.route("/config")
def config():
    """
    Downloads the configuration file.
    ---
    responses:
        200:
            description: Configuration file.
    """
    return send_from_directory("config", "config.json")


@api_bp.route("/tasks")
def tasks():
    """
    Downloads the tasks file.
    ---
    responses:
        200:
            description: Tasks file.
    """
    return send_from_directory("config", "tasks.json")


@api_bp.route("/download-points")
def download_points():
    """
    Downloads recorded points for a specific subject.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to download points.
    responses:
        200:
            description: CSV file with recorded points.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    csv_data = ExportService.export_points_csv(subject_id)
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name=f"points_subject_{subject_id}.csv",
            mimetype="text/csv",
        )

    return "Subject not found", 404


@api_bp.route("/download-tasklogs")
def download_tasklogs():
    """
    Downloads task logs recorded for a specific subject.
    ---
    parameters:
        - name: id
          in: query
          type: integer
          required: true
          description: Subject ID to download task logs.
    responses:
        200:
            description: CSV file with recorded task logs.
        404:
            description: Subject not found.
    """
    subject_id = request.args.get("id", type=int)

    csv_data = ExportService.export_tasklogs_csv(subject_id)
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name=f"tasklogs_subject_{subject_id}.csv",
            mimetype="text/csv",
        )
    else:
        return "Subject not found", 404


@api_bp.route("/download-all")
def download_all():
    """
    Downloads recorded points for all subjects in CSV format.
    ---
    responses:
        200:
            description: CSV file with recorded points for all subjects.
        404:
            description: No registered subjects.
    """
    csv_data = ExportService.export_all_points_csv()
    if csv_data:
        return send_file(
            csv_data,
            as_attachment=True,
            download_name="points_all.csv",
            mimetype="text/csv",
        )
    else:
        return "No registered subjects", 404
