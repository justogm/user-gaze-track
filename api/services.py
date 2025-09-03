"""
API services for the user gaze tracking application.
Contains business logic for data processing and database operations.
"""

import csv
import io
from datetime import datetime
import numpy as np
from app.models import db, Sujeto, Punto, Medicion, TaskLog


class SujetoService:
    """Service class for managing subjects (sujetos)."""
    
    @staticmethod
    def get_all_sujetos():
        """Get all subjects with their basic information."""
        sujetos = Sujeto.query.all()
        return [
            {
                "id": sujeto.id,
                "nombre": sujeto.nombre,
                "apellido": sujeto.apellido,
                "edad": sujeto.edad,
            }
            for sujeto in sujetos
        ]
    
    @staticmethod
    def get_sujeto_by_id(sujeto_id):
        """Get a subject by its ID."""
        return Sujeto.query.filter_by(id=sujeto_id).first()


class MedicionService:
    """Service class for managing measurements (mediciones)."""
    
    @staticmethod
    def save_puntos(data):
        """Save measurement points to the database."""
        puntos = data["puntos"]
        sujeto_id = data["id"]

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
                sujeto_id=sujeto_id,
                punto_gaze=punto_gaze,
                punto_mouse=punto_mouse,
            )
            db.session.add(nueva_medicion)

        db.session.commit()
        return {"status": "success"}
    
    @staticmethod
    def get_user_points(sujeto_id):
        """Get measurement points for a specific subject."""
        sujeto = SujetoService.get_sujeto_by_id(sujeto_id)
        
        if not sujeto:
            return None
        
        mediciones = Medicion.query.filter_by(sujeto_id=sujeto.id).all()
        
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

        return {"sujeto_id": sujeto_id, "puntos": puntos}


class TaskLogService:
    """Service class for managing task logs."""
    
    @staticmethod
    def save_tasklogs(data):
        """Save task logs to the database."""
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
        return {"status": "success", "message": "TaskLogs guardados exitosamente."}
    
    @staticmethod
    def get_user_tasklogs(sujeto_id):
        """Get task logs for a specific subject."""
        sujeto = SujetoService.get_sujeto_by_id(sujeto_id)
        
        if not sujeto:
            return None
        
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
        return {"sujeto_id": sujeto_id, "task_logs": task_logs_info}


class ExportService:
    """Service class for data export functionality."""
    
    @staticmethod
    def export_puntos_csv(sujeto_id):
        """Export measurement points for a subject as CSV."""
        sujeto = SujetoService.get_sujeto_by_id(sujeto_id)
        
        if not sujeto:
            return None
        
        mediciones = Medicion.query.filter_by(sujeto_id=sujeto.id).all()
        
        si = io.StringIO()
        escritor_csv = csv.writer(si)
        
        # Write headers
        escritor_csv.writerow(["fecha", "x_mouse", "y_mouse", "x_gaze", "y_gaze"])
        
        # Write rows
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
        return io.BytesIO(si.getvalue().encode("utf-8"))
    
    @staticmethod
    def export_tasklogs_csv(sujeto_id):
        """Export task logs for a subject as CSV."""
        sujeto = SujetoService.get_sujeto_by_id(sujeto_id)
        
        if not sujeto:
            return None
        
        si = io.StringIO()
        escritor_csv = csv.writer(si)
        
        # Write headers
        escritor_csv.writerow(["start_time", "end_time", "response"])
        
        # Get task logs for the subject
        task_logs = TaskLog.query.filter_by(sujeto_id=sujeto_id).all()
        
        # Write rows
        for log in task_logs:
            fila = [
                log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                log.end_time.strftime("%Y-%m-%d %H:%M:%S") if log.end_time else None,
                log.response,
            ]
            escritor_csv.writerow(fila)
        
        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
    
    @staticmethod
    def export_all_puntos_csv():
        """Export measurement points for all subjects as CSV."""
        all_sujetos = Sujeto.query.all()
        
        if len(all_sujetos) == 0:
            return None
        
        si = io.StringIO()
        escritor_csv = csv.DictWriter(si, fieldnames=["id", "x", "y"])
        escritor_csv.writeheader()

        for sujeto in all_sujetos:
            puntos = Punto.query.filter_by(sujeto_id=sujeto.id).all()
            puntos_dict = [punto.__json__() for punto in puntos]

            id_sujeto = int(sujeto.id)

            puntos_np = np.array([[id_sujeto, p["x"], p["y"]] for p in puntos_dict])

            for punto in puntos_np:
                escritor_csv.writerow({"id": punto[0], "x": punto[1], "y": punto[2]})

        si.seek(0)
        return io.BytesIO(si.getvalue().encode("utf-8"))
