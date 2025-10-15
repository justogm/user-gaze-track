from flask import Flask

app = Flask("server")
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

class AppConfig:
    """Configuración general de la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    
class EmailConfig:
    """Configuración del servidor de correo"""
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    NAME_SENDER = os.getenv('NAME_SENDER')      # NOTE: NAME_SENDER es el nombre que verá el destinatario
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # TODO: Borrar esto si no se utiliza
    # def to_dict():
    #     return {key: getattr(EmailConfig, key) for key in dir(EmailConfig) if key.isupper()}

class BaseUrlConfig:
    """Configuración de URLs"""
    BASE_URL = os.getenv('BASE_URL')

if __name__ == "__main__":
    print(EmailConfig.to_dict())