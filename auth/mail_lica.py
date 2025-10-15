from modules.auth.mail_base import MailBase
from modules.auth.config import EmailConfig
from sender import Mail, Message, Attachment


class MailLICA(MailBase):
    def __init__(self):
        super().__init__()
        self.__mail = None

    def init_mail(self, config: EmailConfig = EmailConfig):
        # Configuración de conexión al servidor SMTP
        SMTP_HOST = EmailConfig.MAIL_SERVER
        SMTP_PORT = EmailConfig.MAIL_PORT
        SMTP_USER = EmailConfig.MAIL_USERNAME
        SMTP_PASS = EmailConfig.MAIL_PASSWORD
        SMTP_ADDRESS = EmailConfig.MAIL_USERNAME # 'sender@example.com'
        NAME_SENDER = EmailConfig.NAME_SENDER
        FROM_ADDR = (NAME_SENDER, SMTP_ADDRESS)   # NOTE: NAME_SENDER es el nombre que verá el destinatario
        MAIL_USE_TLS = EmailConfig.MAIL_USE_TLS

        # Creación de objeto Mail
        self.__mail = Mail(
            host=SMTP_HOST, 
            port=SMTP_PORT, 
            username=SMTP_USER, 
            password=SMTP_PASS, 
            fromaddr=FROM_ADDR,
            use_tls=MAIL_USE_TLS)
    
    def send(self, to_email: str, subject: str, body: str, logo_image_file: str = None):
        html = body # NOTE: texto plano ó HTML
        msg = Message(subject=subject, to=to_email, html=html)
        if logo_image_file is not None:
            with open(logo_image_file, mode="rb") as f:
                attachment = Attachment(logo_image_file.split('/')[-1], "image/jpeg", f.read())
            msg.attach(attachment)
        self.__mail.send(msg)


if __name__ == "__main__":
    mail = MailLICA()
    mail.init_mail()
    # Envío de mensaje de prueba
    to_email = "<nombre@mail.com>" # TODO: Cambiar a tu correo de prueba personal.
    subject  = "Correo con HTML y un logo adjunto con formato JPEG."
    html     = "<h1>Correo con HTML</h1><p style='color:blue;'>¡Hola email!</p>"
    logo_image_file = "apps/ejemplo_sender_00_enviar_correo/logo.jpeg"
    mail.send(to_email, subject, html, logo_image_file)

