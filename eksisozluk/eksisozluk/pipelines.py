import os
import json, re
from datetime import timezone
from scrapy.utils.project import get_project_settings
from eksisozluk.utils.error_tracker import ErrorTracker
from eksisozluk.utils.es_helper import send_stat_to_elasticsearch
from eksisozluk.utils.mailler import send_warning_email
from eksisozluk.utils.logger import get_logger
from datetime import datetime

import requests


logger = get_logger()
settings = get_project_settings()

DT_PATTERNS = [
    "%d.%m.%Y %H:%M",
    "%d.%m.%Y",
]

# --- Session timestamp'ı ayarla ---
session_timestamp = settings.get("SESSION_TIMESTAMP")  # örn: "20251006_181620"


class JsonWriterPipeline:
    def open_spider(self, spider):
        output_dir = os.getenv("JSON_OUTPUT_DIR", "outputs")
        target_dir = os.path.join(output_dir, spider.folder_name_data)
        os.makedirs(target_dir, exist_ok=True)

        self.filepath = os.path.join(target_dir, f"{spider.file_tag}_{session_timestamp}.json")
        self.file = open(self.filepath, "w", encoding="utf-8")
        self.file.write("[\n")
        self.first_item = True

    def close_spider(self, spider):
        self.file.write("\n]")
        self.file.close()

    def process_item(self, item, spider):
        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        line = json.dumps(dict(item), ensure_ascii=False, indent=4)
        self.file.write(line)

        return item


class MediaPipeline:
    media_api = settings.get("MEDIA_API")
    media_api_key = settings.get("MEDIA_API_KEY")

    def __init__(self):
        self.items_buffer = []

    def process_item(self, item, spider):

        common_fields = {
            "source": "Eksi Sozluk",
            "account_url": item.get("account_url"),
            "username": item.get("username"),
            "created_at": item.get("created_at"),
            "scraped_at": item.get("scraped_at"),
            "media_class": "avatar",
            "type": "image",
        }

        avatar_url = item.get("avatar")
        if avatar_url:
            if not avatar_url.startswith("http"):
                avatar_url = f"https:{avatar_url}"
            avatar_entry = {
                **common_fields,
                "url": avatar_url,                
            }
            self.items_buffer.append(avatar_entry)

        logger.info(f"[MediaPipeline] Medyaya gönderilen kayıt: {self.items_buffer[-1] if self.items_buffer else 'Yok'}")
        return item

    def close_spider(self, spider):
        if not self.items_buffer:
            return

        payload = {"items": self.items_buffer}
        try:
            headers = {
                "X-Api-Key": self.media_api_key,
                "Content-Type": "application/json",
                }
            resp = requests.post(self.media_api, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            logger.info(f"[MediaPipeline] {len(self.items_buffer)} item başarıyla gönderildi.")
        except Exception as e:
            ErrorTracker.track(e, context="[MediaPipeline] API gönderim hatası")
            

class StatisticsPipeline:
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.start_time = datetime.now()

    def process_item(self, item, spider):
        self.success_count += 1
        return item

    def close_spider(self, spider):
        end_time = datetime.now()
        duration = end_time - self.start_time
        data_count = self.success_count + self.fail_count
        success_rate = self.success_count / data_count if data_count > 0 else 0
        fail_rate = self.fail_count / data_count if data_count > 0 else 0

        stat_doc = {
            "timestamp": datetime.now().isoformat(),
            "run_id": f"{spider.name}_{session_timestamp}",
            "source": spider.name,
            "data_count": data_count,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "success_rate": success_rate,
            "fail_rate": fail_rate,
            "duration_seconds": duration.total_seconds(),
            "predicted_total_today": (86400 / duration.total_seconds()) if duration.total_seconds() > 0 else 0,
        }

        logger.info(f"[Pipeline] İstatistikler Elasticsearch'e gönderiliyor...")
        send_stat_to_elasticsearch("spider_stats", stat_doc)
        send_warning_email(success_rate)