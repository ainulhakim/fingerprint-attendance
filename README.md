# Fingerprint Attendance Auto-Pull

Auto-pull data absensi dari fingerprint device (Solution X606-S / X105) dan upload ke Google Sheets.

## Cara Kerja

1. Cek tanggal terakhir data di spreadsheet
2. Pull data dari fingerprint device
3. Filter: hanya ambil data dari tanggal terakhir sampai hari ini
4. Skip data yang sudah ada (anti-duplikat)
5. Upload data baru ke Google Sheets

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Edit Config
Edit `fingerprint_pull.py`, sesuaikan:
- `FINGERPRINT_IP` - IP fingerprint device
- `SHEET_ID` - Google Sheets ID
- `WEB_APP_URL` - Google Apps Script Web App URL

### 3. Setup Google Apps Script
- Buat project di https://script.google.com/
- Copy isi `gas_webapp.js`
- Deploy sebagai Web App (Anyone can access)

### 4. Setup Cron
```bash
# Setiap hari jam 09:00, 11:00, 20:00
0 9,11,20 * * * cd /path/to/app && /path/to/venv/bin/python3 fingerprint_pull.py
```

Atau jalankan:
```bash
bash cron_setup.sh
```

## Struktur Data

| NO | PIN | TANGGAL | JAM | STATUS | BULAN | TAHUN |
|----|-----|---------|-----|--------|-------|-------|

Kolom B-G format **TEXT**.
