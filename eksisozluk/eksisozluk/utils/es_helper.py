from datetime import datetime
import hashlib
from elasticsearch import Elasticsearch, exceptions
from eksisozluk.utils.logger import get_logger

from scrapy.utils.project import get_project_settings

settings = get_project_settings()
session_timestamp = settings.get("SESSION_TIMESTAMP")

logger = get_logger()


def get_es_client():
    """Elasticsearch client oluşturur"""
    es_host = settings.get("ES_HOST")
    es_api_key_encoded = settings.get("ES_API_KEY_ENCODED")

    try:
        es = Elasticsearch(es_host, api_key=es_api_key_encoded, verify_certs=False)
        # Basit bağlantı testi (isteğe bağlı)
        if es.ping():
            logger.info("[ElasticSearch] Elasticsearch bağlantısı başarılı ✅")
        return es
    except Exception as e:
        logger.error(f"[ElasticSearch] Client oluşturulamadı: {e}", exc_info=True)
        return None


def send_stat_to_elasticsearch(index_name: str, document: dict):
    es = get_es_client()
    if es is None:
        logger.error("[ElasticSearch] Elasticsearch client başlatılamadı, veri gönderilemedi.")
        return False

    doc_id = hashlib.md5(f"{index_name}_{datetime.now().isoformat()}".encode()).hexdigest()
    try:
        es.index(index=index_name, id=doc_id, document=document)
        logger.info(f"[ElasticSearch] Belge '{index_name}' indeksine başarıyla eklendi. (id={doc_id[:8]}...)")
        return True

    except exceptions.ConnectionError as e:
        logger.error(f"[ElasticSearch] Bağlantı hatası: {e}")
    except exceptions.AuthenticationException as e:
        logger.error(f"[ElasticSearch] Kimlik doğrulama hatası: {e}")
    except exceptions.TransportError as e:
        logger.error(f"[ElasticSearch] Taşıma hatası: {e}")
    except Exception as e:
        logger.exception(f"[ElasticSearch] Beklenmeyen hata: {e}")

    return False



def send_error_to_elasticsearch(error_type: str, message: str, count: int = 1):
    es = get_es_client()
    es_scrape_error_index = settings.get("ES_SCRAPE_ERROR_INDEX")
    
    if not es:
        return False

    doc_id = hashlib.sha1(f"{error_type}:{message}".encode("utf-8")).hexdigest()

    try:
        es.update(
            index=es_scrape_error_index,
            id=doc_id,
            body={
                "script": {
                    "source": """
                        ctx._source.count += params.count;
                        ctx._source.last_seen = params.last_seen;
                    """,
                    "lang": "painless",
                    "params": {
                        "count": count,
                        "last_seen":session_timestamp
                    },
                },
                "upsert": {
                    "source": "Ekşi Sözlük",
                    "error_type": error_type,
                    "message": message,
                    "count": count,
                    "first_occurrence": datetime.now().isoformat(),
                    "last_occurrence": session_timestamp,
                    "last_occurrence_id": f"nsosyal_{session_timestamp}"
                },
            },
        )
        
        # logger.info(f"[ElasticSearch] Hata kayıtları başarıyla gönderildi")
        
        return True


    except exceptions.NotFoundError:
        logger.error(f"[ElasticSearch] Index bulunamadı: scrape_errors")
    except Exception as e:
        logger.error(f"[ElasticSearch] Hata kaydı gönderilemedi: {e}")
    return False