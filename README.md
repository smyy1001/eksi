# 📘 Ekşi Sözlük Scraper – README

## 🚀 Kurulum

1. `.env` dosyasını kendi ortamınıza uygun olacak şekilde doldurun.

2. Projeyi çalıştırmak için:

```bash
docker compose up --build 
```
---

## 📂 Çıktılar

### 1. Data Files (.jsonl)

Kazınan ham postlar **JSONL formatında** kaydedilir:

---

### 2. Log Files (.log)

Her koşuda özet rapor yazılır:

* Kaç adet alındı
* Toplam süre
* Tekilleştirilmiş hata mesajları
* ..

---

### 3. Hata Yönetimi – `scrape_errors` index

Tüm hatalar `ERROR_REGISTRY` mantığıyla toplanır ve koşu bitiminde **Elasticsearch’e** yazılır. Bu özelliğin çalışması için ES_ENABLED=true olması gerekmektedir.

Örnek döküman:

```json
{
  "source": "Ekşi Sözlük",
  "error_type": "ERROR .. / FATAL .. / WARN ..",
  "message": "HTTP 500 ...",
  "count": 7,
  "error_first_occurance": "2025-09-25T09:12:12Z",
  "error_last_occurance": "2025-09-25T09:13:45Z",
  "last_seen_id": "eksi_20250925_091210"
}
```

---

### 4. Statistics – `spider-stats` index

* **Amaç**: Her scraping koşusunun performans metriklerini Elasticsearch’e kaydetmek.

Kaydedilen metrikler arasında:

* `run_id`: Çalıştırma kimliği (örn. `bsky_20250925_101858`)
* `sources`: Telegram + [] (kanal listesi)
* `data_count`: Bu koşuda toplanan gerçek kayıt sayısı
* `success_rate`: `data_count / intended`
* `duration_seconds`: Çalışma süresi
* vb.



#### 📧 E-Mail Uyarıları

* Eğer son 24 saatteki **başarı oranı (`success_rate`)**, `SUCCES_RATE_LIMIT` değerinin altına düşerse otomatik e-posta gönderilir.
---

### 5. Media API Entegrasyonu

Kazınan tüm fotoğraf ve videolar, toplu olarak **Media API**’a gönderilir.

---
