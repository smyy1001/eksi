# Scrapy settings for eksisozluk project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "eksisozluk"

SPIDER_MODULES = ["eksisozluk.spiders"]
NEWSPIDER_MODULE = "eksisozluk.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "eksisozluk (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "eksisozluk.middlewares.EksisozlukSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "eksisozluk.middlewares.EksisozlukDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "eksisozluk.pipelines.JsonWriterPipeline": 300,
    "eksisozluk.pipelines.MediaPipeline": 300,
    "eksisozluk.pipelines.StatisticsPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"



import datetime

SESSION_TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
SESSION_DATE = datetime.datetime.now().strftime("%Y%m%d")

import os
from dotenv import load_dotenv
from eksisozluk.utils.logger import get_logger

load_dotenv()
env_logger = get_logger(name="env", env_logger=True)

ENV_LOG_INFO = os.getenv("ENV_LOG_INFO", "false").lower() in ("1", "true", "yes")

def safe_getenv(key: str, default=None, required=False, cast=str):
    """
    Ortam değişkenlerini güvenli şekilde alır.
    - key: env değişken adı
    - default: yoksa kullanılacak varsayılan
    - required=True ise env yoksa hata loglar
    - cast: dönüşüm (int, bool vs.)
    Başarılı okumalarda, ENV_LOG_INFO=True ise info log basar.
    """
    value = os.getenv(key, default)

    if value is None:
        if required:
            env_logger.error(f"[ENV] Gerekli env bulunamadı: {key}")
        else:
            env_logger.warning(f"[ENV] {key} bulunamadı, default={default} kullanılıyor")
        return default

    try:
        casted_value = cast(value)
        if ENV_LOG_INFO:
            env_logger.info(f"[ENV] {key} = {casted_value} (tip: {cast.__name__})")
        return casted_value
    except Exception as e:
        env_logger.error(f"[ENV] {key} dönüşüm hatası ({value} -> {cast}): {e}")
        return default
    
def log_section(title: str):
    """Sadece ENV_LOG_INFO=True olduğunda bölüm başlıklarını loglar."""
    if ENV_LOG_INFO:
        env_logger.info(f"===== {title} =====")

# =============================
# ENV değerleri
# =============================

# JSON & Log dosyaları
log_section("OUTPUT PATHS")
JSON_OUTPUT_DIR = safe_getenv("JSON_OUTPUT_DIR")
LOG_OUTPUT_DIR = safe_getenv("LOG_OUTPUT_DIR")

# Elasticsearch
log_section("ELASTIC SEARCH")
ES_HOST = safe_getenv("ES_HOST")
ES_API_KEY_ENCODED = safe_getenv("ES_API_KEY_ENCODED")
ES_SCRAPE_ERROR_INDEX = safe_getenv("ES_SCRAPE_ERROR_INDEX")

# Mail Ayarları
log_section("MAILLER")
SMTP_SERVER = safe_getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = safe_getenv("SMTP_PORT", 587, cast=int)
FROM_EMAIL = safe_getenv("FROM_EMAIL", required=True)
FROM_PASSWORD = safe_getenv("FROM_PASSWORD", required=True)
TO_EMAIL = safe_getenv("TO_EMAIL", required=True)
SUCCES_RATE_LIMIT = safe_getenv("SUCCES_RATE_LIMIT", 0.75, cast=float)

# PostgreSQL
log_section("POSTGRE SQL")
PGHOST = safe_getenv("PGHOST", "localhost")
PGPORT = safe_getenv("PGPORT", 5432, cast=int)
PGUSER = safe_getenv("PGUSER", "postgres")
PGPASSWORD = safe_getenv("PGPASSWORD", "")
PGDATABASE = safe_getenv("PGDATABASE", "postgres")


log_section("Media API")
MEDIA_API = safe_getenv("MEDIA_API")
MEDIA_API_KEY = safe_getenv("MEDIA_API_KEY")