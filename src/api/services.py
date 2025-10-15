"""
API services for the user gaze tracking application.
Contains business logic for data processing and database operations.
"""

import csv
import io
from datetime import datetime
import numpy as np
from app.models import db, Subject, Point, Measurement, TaskLog


class SubjectService:
    """Service class for managing subjects."""

    @staticmethod
    def get_all_subjects():
        """Get all subjects with their basic information."""
        subjects = Subject.query.all()
        return [
            {
                "id": subject.id,
                "name": subject.name,
                "surname": subject.surname,
                "age": subject.age,
            }
            for subject in subjects
        ]

    @staticmethod
    def get_subject_by_id(subject_id):
        """Get a subject by its ID."""
        return Subject.query.filter_by(id=subject_id).first()


class MeasurementService:
    """Service class for managing measurements."""

    @staticmethod
    def save_points(data):
        """Save measurement points to the database."""
        points = data["points"]
        subject_id = data["id"]

        for point in points:
            date = datetime.strptime(point["date"], "%m/%d/%Y, %I:%M:%S %p")

            gaze_point = Point(
                x=point["gaze"]["x"],
                y=point["gaze"]["y"],
            )
            db.session.add(gaze_point)

            mouse_point = Point(
                x=point["mouse"]["x"],
                y=point["mouse"]["y"],
            )
            db.session.add(mouse_point)

            new_measurement = Measurement(
                date=date,
                subject_id=subject_id,
                gaze_point=gaze_point,
                mouse_point=mouse_point,
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

        measurements = Measurement.query.filter_by(subject_id=subject.id).all()

        points = []
        for measurement in measurements:
            point = {
                "date": measurement.date.strftime("%Y-%m-%d %H:%M:%S"),
                "x_mouse": (
                    measurement.mouse_point.x if measurement.mouse_point else None
                ),
                "y_mouse": (
                    measurement.mouse_point.y if measurement.mouse_point else None
                ),
                "x_gaze": measurement.gaze_point.x if measurement.gaze_point else None,
                "y_gaze": measurement.gaze_point.y if measurement.gaze_point else None,
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
                subject_id=subject_id,
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

        task_logs = TaskLog.query.filter_by(subject_id=subject.id).all()
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

        measurements = Measurement.query.filter_by(subject_id=subject.id).all()

        si = io.StringIO()
        csv_writer = csv.writer(si)

        csv_writer.writerow(["date", "x_mouse", "y_mouse", "x_gaze", "y_gaze"])

        for measurement in measurements:
            row = [
                measurement.date.strftime("%Y-%m-%d %H:%M:%S"),
                measurement.mouse_point.x if measurement.mouse_point else None,
                measurement.mouse_point.y if measurement.mouse_point else None,
                measurement.gaze_point.x if measurement.gaze_point else None,
                measurement.gaze_point.y if measurement.gaze_point else None,
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

        csv_writer.writerow(["start_time", "end_time", "response"])

        task_logs = TaskLog.query.filter_by(subject_id=subject_id).all()

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
        all_subjects = Subject.query.all()

        if len(all_subjects) == 0:
            return None

        si = io.StringIO()
        csv_writer = csv.DictWriter(si, fieldnames=["id", "x", "y"])
        csv_writer.writeheader()

        for subject in all_subjects:
            points = Point.query.filter_by(subject_id=subject.id).all()
            points_dict = [point.__json__() for point in points]

            subject_id = int(subject.id)

            points_np = np.array([[subject_id, p["x"], p["y"]] for p in points_dict])

            for point in points_np:
                csv_writer.writerow({"id": point[0], "x": point[1], "y": point[2]})

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
