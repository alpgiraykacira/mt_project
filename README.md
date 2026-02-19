# MT Dashboard - Skorkart Yönetim Platformu

Model envanteri yönetimi ve skorkart geliştirme süreçlerinin takibi için interaktif dashboard.

## Teknoloji

- **Backend:** Flask + SQLAlchemy (Oracle DB / SQLite)
- **Frontend:** Vue 3 + Vite + PrimeVue + Chart.js
- **API:** RESTful JSON

## Kurulum

### Backend

```bash
cd backend
pip install -r requirements.txt

# .env dosyasını oluştur
cp .env.example .env
# Oracle bağlantısı için DATABASE_URL değişkenini güncelle

# Geliştirme sunucusu
python app.py

# Demo verisi yükle (opsiyonel)
python seed_data.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Uygulama `http://localhost:5173` adresinde çalışır. Backend API proxy olarak `http://localhost:5000` adresine yönlendirilir.

## Oracle DB Bağlantısı

`.env` dosyasında `DATABASE_URL` değişkenini Oracle bağlantı string'i ile güncelleyin:

```
DATABASE_URL=oracle+oracledb://username:password@hostname:1521/?service_name=ORCL
```

## Modüller

### Mevcut Skorkartlar
- Model Envanteri (ad, tür, segment, Gini skorları, durum)
- Teknik Kılavuz (sorgular, değişken hesaplamaları, metodoloji)
- Validasyon Raporları (giden/gelen dosyalar)
- Gini Geçmişi (trend grafikleri)

### Geliştirilen Skorkartlar
- Proje takibi (owner bazında ilerleme)
- Geliştirme aşamaları (varsayılan 8 aşama şablonu)
- Görev yönetimi (aşama içi checklist)
- Deadline takibi ve gecikme uyarıları
