from abc import ABC, abstractmethod

class EmailService(ABC):
    
    @abstractmethod
    def send_credentials_email(self, to_email: str, username: str, password: str, nombre_completo: str) -> bool:
        pass
