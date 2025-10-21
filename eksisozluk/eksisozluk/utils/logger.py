import logging
import os
from dotenv import load_dotenv
from scrapy.utils.project import get_project_settings

load_dotenv()

def get_logger(name="eksisozluk", env_logger=False):
    

    settings = get_project_settings()
    session_date = settings.get( "SESSION_DATE" )

    log_output_dir = os.getenv("LOG_OUTPUT_DIR", "logs")
    os.makedirs(log_output_dir, exist_ok=True)

    # ENV_LOG_INFO kontrolü
    env_log_info = os.getenv("ENV_LOG_INFO", "false").lower() in ("1", "true", "yes")

    log_file = os.path.join(log_output_dir, f"eksisozluk_{session_date}.log")
    env_log_file = os.path.join(log_output_dir, f"ENV_eksisozluk_{session_date}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        if env_logger:
            if env_log_info:  # sadece ENV_LOG_INFO=True ise ENV log dosyası aç
                file_handler = logging.FileHandler(env_log_file, encoding="utf-8")
            else:
                return logger  # ENV log aktif değilse handler ekleme
        else:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")

        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
