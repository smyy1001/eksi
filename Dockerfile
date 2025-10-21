FROM python:3.10-slim

ENV TZ=Europe/Istanbul

WORKDIR /app

# Gereken paketler
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Ortam değişkenleri için .env dosyası kullanılacak (docker-compose ayarlıyor)
