from abc import ABC, abstractmethod


class MailBase(ABC):
    @abstractmethod
    def send(self, to_email: str, subject: str, body: str, logo_image_file: str = None):
        pass