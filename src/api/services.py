"""
API services for the user gaze tracking application.
Contains business logic for data processing and database operations.
"""

import csv
import io
from datetime import datetime
import numpy as np
from app.models import db, Sujeto, Punto, Medicion, TaskLog


class SubjectService:
    """Service class for managing subjects."""
    
    @staticmethod
    def get_all_subjects():
        """Get all subjects with their basic information."""
        subjects = Sujeto.query.all()
        return [
            {
                "id": subject.id,
                "name": subject.nombre,
                "surname": subject.apellido,
                "age": subject.edad,
            }
            for subject in subjects
        ]
    
    @staticmethod
    def get_subject_by_id(subject_id):
        """Get a subject by its ID."""
        return Sujeto.query.filter_by(id=subject_id).first()


class MeasurementService:
    """Service class for managing measurements."""
    
    @staticmethod
    def save_points(data):
        """Save measurement points to the database."""
        points = data["points"]
        subject_id = data["id"]

        for point in points:
            date = datetime.strptime(point["date"], "%m/%d/%Y, %I:%M:%S %p")
            
            gaze_point = Punto(
                x=point["gaze"]["x"],
                y=point["gaze"]["y"],
            )
            db.session.add(gaze_point)

            mouse_point = Punto(
                x=point["mouse"]["x"],
                y=point["mouse"]["y"],
            )
            db.session.add(mouse_point)

            new_measurement = Medicion(
                fecha=date,
                sujeto_id=subject_id,
                punto_gaze=gaze_point,
                punto_mouse=mouse_point,
            )
            db.session.add(new_measurement)

        db.session.commit()
        return {"status": "success"}
    
    @staticmethod
    def get_user_points(subject_id):
        """Get measurement points for a specific subject."""
        subject = SubjectService.get_subject_by_id(subject_id)
        
        if not subject:
            return None
        
        measurements = Medicion.query.filter_by(sujeto_id=subject.id).all()

        points = []
        for measurement in measurements:
            point = {
                "date": measurement.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "x_mouse": measurement.punto_mouse.x if measurement.punto_mouse else None,
                "y_mouse": measurement.punto_mouse.y if measurement.punto_mouse else None,
                "x_gaze": measurement.punto_gaze.x if measurement.punto_gaze else None,
                "y_gaze": measurement.punto_gaze.y if measurement.punto_gaze else None,
            }
            points.append(point)


        return {"subject_id": subject_id, "points": points}


class TaskLogService:
    """Service class for managing task logs."""
    
    @staticmethod
    def save_tasklogs(data):
        """Save task logs to the database."""
        task_logs = data["taskLogs"]
        subject_id = data["subject_id"]

        for log in task_logs:
            new_log = TaskLog(
                start_time=datetime.strptime(log["startTime"], "%m/%d/%Y, %I:%M:%S %p"),
                end_time=(
                    datetime.strptime(log["endTime"], "%m/%d/%Y, %I:%M:%S %p")
                    if log["endTime"]
                    else None
                ),
                response=log["response"],
                sujeto_id=subject_id,
            )
            db.session.add(new_log)

        db.session.commit()
        return {"status": "success", "message": "TaskLogs saved successfully."}
    
    @staticmethod
    def get_user_tasklogs(subject_id):
        """Get task logs for a specific subject."""
        subject = SubjectService.get_subject_by_id(subject_id)
        
        if not subject:
            return None
        
        task_logs = TaskLog.query.filter_by(sujeto_id=subject.id).all()
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
        return {"subject_id": subject_id, "task_logs": task_logs_info}


class ExportService:
    """Service class for data export functionality."""
    
    @staticmethod
    def export_points_csv(subject_id):
        """Export measurement points for a subject as CSV."""
        subject = SubjectService.get_subject_by_id(subject_id)
        
        if not subject:
            return None
        
        measurements = Medicion.query.filter_by(sujeto_id=subject.id).all()
        
        si = io.StringIO()
        csv_writer = csv.writer(si)
        
        # Write headers
        csv_writer.writerow(["date", "x_mouse", "y_mouse", "x_gaze", "y_gaze"])
        
        # Write rows
        for measurement in measurements:
            row = [
                measurement.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                measurement.punto_mouse.x if measurement.punto_mouse else None,
                measurement.punto_mouse.y if measurement.punto_mouse else None,
                measurement.punto_gaze.x if measurement.punto_gaze else None,
                measurement.punto_gaze.y if measurement.punto_gaze else None,
            ]
            csv_writer.writerow(row)
        
        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
    
    @staticmethod
    def export_tasklogs_csv(subject_id):
        """Export task logs for a subject as CSV."""
        subject = SubjectService.get_subject_by_id(subject_id)
        
        if not subject:
            return None
        
        si = io.StringIO()
        csv_writer = csv.writer(si)
        
        # Write headers
        csv_writer.writerow(["start_time", "end_time", "response"])
        
        # Get task logs for the subject
        task_logs = TaskLog.query.filter_by(sujeto_id=subject_id).all()
        
        # Write rows
        for log in task_logs:
            row = [
                log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                log.response,
            ]
            csv_writer.writerow(row)
        
        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
    
    @staticmethod
    def export_all_points_csv():
        """Export measurement points for all subjects as CSV."""
        all_subjects = Sujeto.query.all()
        
        if len(all_subjects) == 0:
            return None
        
        si = io.StringIO()
        csv_writer = csv.DictWriter(si, fieldnames=["id", "x", "y"])
        csv_writer.writeheader()

        for subject in all_subjects:
            points = Punto.query.filter_by(sujeto_id=subject.id).all()
            points_dict = [point.__json__() for point in points]

            subject_id = int(subject.id)

            points_np = np.array([[subject_id, p["x"], p["y"]] for p in points_dict])

            for point in points_np:
                csv_writer.writerow({"id": point[0], "x": point[1], "y": point[2]})

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
