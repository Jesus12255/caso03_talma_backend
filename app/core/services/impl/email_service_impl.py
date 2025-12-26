import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.services.email_service import EmailService
from config.config import settings
import logging

class EmailServiceImpl(EmailService):
    
    def __init__(self):
        self.smtp_host = settings.MAIL_HOST
        self.smtp_port = settings.MAIL_PORT
        self.smtp_user = settings.MAIL_USER
        self.smtp_password = settings.MAIL_PASSWORD
        self.logger = logging.getLogger(__name__)

    def send_credentials_email(self, to_email: str, username: str, password: str, nombre_completo: str) -> bool:
        print(f"DEBUG: Preparing to send email to {to_email} via {self.smtp_host}:{self.smtp_port} user={self.smtp_user}") # Debug
        try:
            msg = MIMEMultipart("alternative")
            msg['Subject'] = "Bienvenido a TALMA - Credenciales de Acceso"
            msg['From'] = f"TALMA System <{self.smtp_user}>" # Or a noreply address if configured
            msg['To'] = to_email

            html_content = f"""
            <!doctype html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <style>
                    body {{ font-family: sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; border-bottom: 2px solid #D7282F; padding-bottom: 20px; margin-bottom: 20px; }}
                    .logo {{ font-size: 24px; font-weight: bold; color: #D7282F; }}
                    .content {{ color: #333333; line-height: 1.6; }}
                    .credentials {{ background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 15px; margin: 20px 0; }}
                    .label {{ font-weight: bold; color: #555555; }}
                    .value {{ font-family: monospace; font-size: 16px; color: #000000; }}
                    .footer {{ text-align: center; font-size: 12px; color: #888888; margin-top: 30px; border-top: 1px solid #eeeeee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">TALMA</div>
                    </div>
                    <div class="content">
                        <h2>¡Bienvenido, {nombre_completo}!</h2>
                        <p>Su cuenta ha sido creada exitosamente en el sistema TALMA.</p>
                        <p>A continuación, encontrará sus credenciales de acceso:</p>
                        
                        <div class="credentials">
                            <p><span class="label">Usuario:</span> <span class="value">{username}</span></p>
                            <p><span class="label">Contraseña:</span> <span class="value">{password}</span></p>
                        </div>
                        
                        <p>Por seguridad, le recomendamos cambiar su contraseña al iniciar sesión por primera vez.</p>
                    </div>
                    <div class="footer">
                        <p>Este es un mensaje automático, por favor no responda a este correo.</p>
                        <p>&copy; 2024 TALMA. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            part1 = MIMEText(html_content, "html")
            msg.attach(part1)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            
            self.logger.info(f"Email credentials sent to {to_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            # print(f"Failed to send email: {e}") # For debugging locally if needed
            return False

    def send_verification_code(self, to_email: str, code: str, nombre_completo: str) -> bool:
        print(f"DEBUG: Preparing to send verification code to {to_email} via {self.smtp_host}:{self.smtp_port}")
        try:
            msg = MIMEMultipart("alternative")
            msg['Subject'] = f"{code} es su código de verificación de TALMA"
            msg['From'] = f"TALMA System <{self.smtp_user}>"
            msg['To'] = to_email

            html_content = f"""
            <!doctype html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                <style>
                    body {{ font-family: sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; border-bottom: 2px solid #D7282F; padding-bottom: 20px; margin-bottom: 20px; }}
                    .logo {{ font-size: 24px; font-weight: bold; color: #D7282F; }}
                    .content {{ color: #333333; line-height: 1.6; text-align: center; }}
                    .code-container {{ background-color: #f8f9fa; border: 2px dashed #D7282F; border-radius: 8px; padding: 20px; margin: 25px 0; }}
                    .code {{ font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: bold; color: #D7282F; letter-spacing: 5px; }}
                    .footer {{ text-align: center; font-size: 12px; color: #888888; margin-top: 30px; border-top: 1px solid #eeeeee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">TALMA</div>
                    </div>
                    <div class="content">
                        <h2>Verificación de Cuenta</h2>
                        <p>Hola {nombre_completo},</p>
                        <p>Has solicitado un código de verificación para acceder o realizar cambios en tu cuenta.</p>
                        <p>Utiliza el siguiente código para completar el proceso:</p>
                        
                        <div class="code-container">
                            <span class="code">{code}</span>
                        </div>
                        
                        <p>Este código es válido por tiempo limitado. Si no has solicitado este código, puedes ignorar este mensaje.</p>
                    </div>
                    <div class="footer">
                        <p>Este es un mensaje automático, por favor no responda a este correo.</p>
                        <p>&copy; 2024 TALMA. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            part1 = MIMEText(html_content, "html")
            msg.attach(part1)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, msg.as_string())
            
            self.logger.info(f"Verification code sent to {to_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send verification code to {to_email}: {str(e)}")
            return False
