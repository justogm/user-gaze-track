from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sujeto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

class Trayectoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sujeto_id = db.Column(db.Integer, db.ForeignKey('sujeto.id'), nullable=False)

class Punto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    trayectoria_id = db.Column(db.Integer, 
                               db.ForeignKey('trajectory.id'), 
                               nullable=False)

    def __str__(self):
        return f'Punto ({self.coordenada_x}, {self.coordenada_y})'