import datetime
import scrapy
from eksisozluk.utils.parse_helper import EksiSelectors
from eksisozluk.utils.parse_helper import parse_entry
from eksisozluk.utils.error_tracker import ErrorTracker
from eksisozluk.utils.logger import get_logger
from scrapy.utils.project import get_project_settings
from eksisozluk.utils.url_builders import build_static_gundem_url

logger = get_logger()

settings = get_project_settings()
session_timestamp = settings.get("SESSION_TIMESTAMP")

class EksiSpider(scrapy.Spider):
    name = "eksi_sozluk"
    file_tag = "eksi_sozluk"
    folder_name_data = "eksisozluk_gundem_data"
    folder_name_log = "eksisozluk_gundem_log"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_count = 0
        self.fail_count = 0
        self.start_time = datetime.datetime.now()

    def start_requests(self):
        
        logger.info(f"##############################################################################")
        logger.info(f"######### Ekşi Sözlük Gündem oturum başlama zamanı : {session_timestamp} #########")
        logger.info(f"##############################################################################")
        
        
        try:
            urls = build_static_gundem_url()
            if not urls:
                logger.warning("[SPIDER] build_static_gundem_url() boş döndü!")

            for url in urls:
                yield scrapy.Request(
                    url=url,
                    headers=self.headers,
                    callback=self.parse_topic_list,
                    errback=self.handle_request_error,
                )

        except Exception as e:
            ErrorTracker.track(e, context="[SPIDER] start_requests hata", exc_info=True)

    def parse_topic_list(self, response):
        try:
            titles = response.xpath(EksiSelectors.TOPIC_LIST)
            if not titles:
                logger.warning(f"[SPIDER] Sayfada Gündem bulunamadı: {response.url}")

            for title in titles:
                title_url = response.urljoin(title.xpath("@href").get())
                yield scrapy.Request(
                    url=title_url,
                    headers=self.headers,
                    callback=self.parse_content,
                    errback=self.handle_request_error,
                )

        except Exception as e:
            ErrorTracker.track(e, context=f"[SPIDER] hata: {e} | URL: {response.url}")
            self.fail_count += 1

    def parse_content(self, response):
        try:
            entries = response.xpath(EksiSelectors.ENTRY_LIST)
            if not entries:
                logger.warning(f"[SPIDER] Entry bulunamadı: {response.url}")

            for entry in entries[:1]:
                try:
                    item = parse_entry(entry, response)
                    self.success_count += 1
                    yield item
                except Exception as inner_e:
                    logger.error(
                        f"[SPIDER -> parse_entry] Hata: {inner_e} | URL: {response.url}",
                        exc_info=True,
                    )
                    ErrorTracker.track(inner_e)
                    self.fail_count += 1

            # Sayfalandırma
            current_page = response.xpath(EksiSelectors.PAGER_CURRENT).get()
            total_pages = response.xpath(EksiSelectors.PAGER_TOTAL).get()
            if current_page and total_pages:
                try:
                    current_page = int(current_page)
                    total_pages = int(total_pages)
                    if current_page < total_pages:
                        next_page_url = self.get_next_page_url(
                            response.url, current_page + 1
                        )
                        yield scrapy.Request(
                            url=next_page_url,
                            headers=self.headers,
                            callback=self.parse_content,
                            errback=self.handle_request_error,
                        )
                except Exception as pg_e:
                    logger.error(
                        f"[SPIDER -> pagination] Hata: {pg_e} | URL: {response.url}",
                        exc_info=True,
                    )
                    ErrorTracker.track(pg_e)

        except Exception as e:
            logger.error(f"[parse_content] hata: {e} | URL: {response.url}", exc_info=True)
            ErrorTracker.track(e)
            self.fail_count += 1

    def get_next_page_url(self, url, next_page_number):
        base_url = url.split("&p=")[0]
        return f"{base_url}&p={next_page_number}"
    
    
    def handle_request_error(self, failure):
        self.fail_count += 1
        error_msg = repr(failure.value)
        request_url = getattr(failure.request, "url", "Bilinmiyor")
        logger.error(f"[handle_request_error] {error_msg} | URL: {request_url}")
        ErrorTracker.track(failure.value)


    def closed(self, reason):
        duration = datetime.datetime.now() - self.start_time
        ErrorTracker.report()
        ErrorTracker.reset()

        logger.info(f"[Spider] {self.name} kapandı ({reason}) | Başarılı: {self.success_count}, Başarısız: {self.fail_count}, Süre: {duration.total_seconds():.2f}s")