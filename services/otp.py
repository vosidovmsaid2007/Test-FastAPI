import random
import smtplib
import string
from email.mime.text import MIMEText

from utils.log import Logger

class EMAIL:
    URL_SERVER = "http://localhost:8000/users/verify?token="
    LOGIN = "msaidvosidov@gmail.com"
    PASSWORD = "fpxs qnsc ivfk hoqt"

class EmailOTPService:

    @staticmethod
    async def generate_otp() -> str:
        code = ""
        for _ in range(4):
            code += random.choice(string.digits)
        return code

    async def send_otp(self, recipient: str, token: str) -> bool:
        subject = "Your verification code "
        body = f"""
                <html>
                    <body>
                        Для подтверждения аккаунта нажмите на ссылку: <a href="{EMAIL.URL_SERVER}{token}"><b>Ссылка</b></a>
                    </body>
                </html>
        """
        return self._send_email(recipient, subject, body)

    def _send_email(self, recipient: str, subject: str, message: str) -> bool:
        msg = MIMEText(message, "html")
        msg["Subject"] = subject
        msg["From"] = "Verification Service | Msaid"
        msg["To"] = recipient
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp_server:
            try:
                smtp_server.starttls()
                smtp_server.login(EMAIL.LOGIN, EMAIL.PASSWORD)
                smtp_server.send_message(msg)
            except Exception as ex:
                Logger.info(f"Cannot send message! Error: {ex.__str__()}")
                return False
            else:
                return True
