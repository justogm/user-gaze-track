from flask_session import Session

def init_session(app):
    Session(app)
