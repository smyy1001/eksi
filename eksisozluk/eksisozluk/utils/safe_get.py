# safe_get.py
from collections import Counter
from eksisozluk.utils.error_tracker import ErrorTracker
from eksisozluk.utils.logger import get_logger

logger = get_logger()
missing_counter = Counter()


def safe_xpath_get(selector, xpath: str, default=None, context: str = ""):
    """
    Scrapy Selector içinden güvenli şekilde tek değer alır.
    Hata veya eksik veri durumunda log ve hata takibi yapar.
    """
    try:
        value = selector.xpath(xpath).get(default=default)
        if value is None:
            missing_counter[(context, xpath)] += 1
        return value
    except Exception as e:
        ErrorTracker.track(e, context=f"[safe_xpath_get] Hata | XPath: {xpath} | Context: {context} | Hata: {e}", exc_info=True,)
        return default


def safe_xpath_getall(selector, xpath: str, default=None, context: str = ""):
    """
    Scrapy Selector içinden güvenli şekilde liste döndürür.
    """
    try:
        values = selector.xpath(xpath).getall()
        if not values:
            missing_counter[(context, xpath)] += 1
        return values or default
    except Exception as e:
        ErrorTracker.track(e, context=f"[safe_xpath_getall] Hata | XPath: {xpath} | Context: {context} | Hata: {e}", exc_info=True,)
        return default


def safe_xpath_string(selector, xpath: str, default=None, context: str = ""):
    """
    XPath üzerinden string() ile tüm metni çeker, eksik veya hatalıysa loglar.
    """
    try:
        value = selector.xpath(xpath).xpath("string()").get(default=default)
        if value is None:
            missing_counter[(context, xpath)] += 1
        return value.strip() if value else default
    except Exception as e:
        ErrorTracker.track(e, context=f"[safe_xpath_string] Hata | XPath: {xpath} | Context: {context} | Hata: {e}", exc_info=True,)
        return default


def safe_get(data: dict, key: str, default=None, context: str = ""):
    """
    Dictionary üzerinden güvenli şekilde key alır.
    """
    try:
        value = data.get(key, default)
        if value is None:
            missing_counter[(context, key)] += 1
        return value
    except Exception as e:
        ErrorTracker.track(e, context=f"[safe_get] Hata | Key: {key} | Context: {context} | Hata: {e}", exc_info=True,)
        return default