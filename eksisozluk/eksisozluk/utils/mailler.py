# mailler.py
import smtplib
from email.message import EmailMessage
from eksisozluk.utils.error_tracker import ErrorTracker
from eksisozluk.utils.logger import get_logger

from scrapy.utils.project import get_project_settings

settings = get_project_settings()

SMTP_SERVER = settings.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(settings.get("SMTP_PORT", 587))  # TLS için 587, SSL için 465
FROM_EMAIL = settings.get("FROM_EMAIL")
FROM_PASSWORD = settings.get("FROM_PASSWORD")
TO_EMAIL = settings.get("TO_EMAIL")
SUCCES_RATE_LIMIT = settings.get("SUCCES_RATE_LIMIT", "0.5")

logger = get_logger()

def send_warning_email(success_rate: float):

    if success_rate >= SUCCES_RATE_LIMIT:
        return  # mail gönderme, eşik aşılmamış

    subject = "UYARI: Ekşi Sözlük Success Rate Çok Düşük"
    body = (
        f"Merhaba,\n\n"
        f"Ekşi Sözlük örümceğinin success rate'i kritik seviyenin altına düştü.\n"
        f"Aktif success_rate: {success_rate:.2%}\n\n"
        f"Lütfen sistemi kontrol edin."
    )

    try:
        # Mail objesi oluştur
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = TO_EMAIL
        msg.set_content(body)

        # SMTP ile gönder
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS güvenliği
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)

        logger.info("[SuccesRate] : Uyarı maili başarıyla gönderildi.")

    except Exception as e:
        # logger.error(f"[SuccesRate] : Uyarı maili gönderilirken hata oluştu: {e}")
        ErrorTracker.track(e, context="[SuccesRate] : Uyarı maili gönderilirken hata oluştu")
