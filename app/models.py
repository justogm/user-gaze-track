from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Sujeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    edad = db.Column(db.Integer, nullable=False)


class Medicion(db.Model):
    """
    Representa una medición asociada a un sujeto, con puntos específicos para mouse y gaze.
    """

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    sujeto_id = db.Column(db.Integer, db.ForeignKey("sujeto.id"), nullable=False)
    punto_mouse_id = db.Column(db.Integer, db.ForeignKey("punto.id"), nullable=True)
    punto_gaze_id = db.Column(db.Integer, db.ForeignKey("punto.id"), nullable=True)

    punto_mouse = db.relationship("Punto", foreign_keys=[punto_mouse_id])
    punto_gaze = db.relationship("Punto", foreign_keys=[punto_gaze_id])

    def __str__(self):
        return f"Medicion {self.id} - Fecha: {self.fecha}"

    def __json__(self):
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat(),
            "punto_mouse": self.punto_mouse.__json__() if self.punto_mouse else None,
            "punto_gaze": self.punto_gaze.__json__() if self.punto_gaze else None,
        }


class Punto(db.Model):
    """
    Representa un punto genérico en el espacio (x, y).
    """

    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)

    def __str__(self):
        return f"Punto ({self.x}, {self.y})"

    def __json__(self):
        return {"x": self.x, "y": self.y}
