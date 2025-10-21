from collections import Counter
from eksisozluk.utils.logger import get_logger
from eksisozluk.utils.es_helper import send_error_to_elasticsearch
import re

logger = get_logger()


def normalize_message(msg: str) -> str:
    # Python object bellek adreslerini kaldır
    msg = re.sub(r"0x[0-9a-fA-F]+", "0x*", msg)
    return msg


class ErrorTracker:
    _error_counter = Counter()
    _error_messages = []

    @classmethod
    def track(cls, exception: Exception, context: str = None):
        """
        Hata yakalandığında çağrılır.
        Hata tipine göre sayım ve mesaj kaydı yapar.
        
        context: Hata ile birlikte kaydedilecek özel açıklama (örn. "[SuccesRate] : ...")
        """
        err_type = type(exception).__name__
        base_msg = normalize_message(str(exception))

        if context:
            # Context'i başa ekle
            err_msg = f"{context}: {base_msg}"
        else:
            err_msg = base_msg

        cls._error_counter[err_type] += 1
        cls._error_messages.append(err_msg)


    @classmethod
    def report(cls):
        """
        Tüm hata istatistiklerini loglar ve Elasticsearch'e gönderir.
        """
        if not cls._error_counter:
            logger.info("[ErrorTracker] Hata kaydı bulunamadı.")
            return

        logger.error("[ErrorTracker] Veri işleme sırasında hatalar oluştu:")
        

        for err_type, count in cls._error_counter.items():
            logger.error(f" - {err_type}: {count} kez")

            # Elasticsearch'e gönder
            send_error_to_elasticsearch(
                error_type=err_type,
                message="; ".join(set(cls._error_messages)),  # zaten normalize edilmiş
                count=count
            )


        unique_msgs = set(cls._error_messages)
        logger.error("[ErrorTracker] Benzersiz hata mesajları:")
        for msg in unique_msgs:
            logger.error(f"   -> {msg}")

        # Report sonrası reset atmak istersek
        # cls.reset()

    @classmethod
    def reset(cls):
        """Kaydedilen hataları sıfırlar (opsiyonel kullanım için)"""
        cls._error_counter = Counter()
        cls._error_messages = []
