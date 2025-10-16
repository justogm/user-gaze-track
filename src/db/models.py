from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Subject(db.Model):
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)


class Measurement(db.Model):
    """Represents a measurement associated with a subject, with specific points for mouse and gaze."""
    
    __tablename__ = 'measurement'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    mouse_point_id = db.Column(db.Integer, db.ForeignKey("point.id"), nullable=True)
    gaze_point_id = db.Column(db.Integer, db.ForeignKey("point.id"), nullable=True)

    mouse_point = db.relationship("Point", foreign_keys=[mouse_point_id])
    gaze_point = db.relationship("Point", foreign_keys=[gaze_point_id])

    def __str__(self):
        return f"Measurement {self.id} - Date: {self.date}"

    def __json__(self):
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "mouse_point": self.mouse_point.__json__() if self.mouse_point else None,
            "gaze_point": self.gaze_point.__json__() if self.gaze_point else None,
        }


class Point(db.Model):
    """Represents a generic point in space (x, y)."""
    
    __tablename__ = 'point'

    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f"Point ({self.x}, {self.y})"

    def __json__(self):
        return {"x": self.x, "y": self.y}


class TaskLog(db.Model):
    """Represents a log of a task performed by a subject."""
    
    __tablename__ = 'task_log'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    response = db.Column(db.String(255), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)

    subject = db.relationship("Subject", backref=db.backref("task_logs", lazy=True))

    def __str__(self):
        return f"TaskLog {self.id} - Subject: {self.subject_id} - Start: {self.start_time}"

    def __json__(self):
        return {
            "id": self.id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "response": self.response,
            "subject_id": self.subject_id,
        }
