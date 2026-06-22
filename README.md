# Fingerprint Attendance Auto-Pull

Auto-pull data absensi dari fingerprint device (Solution X606-S / X105) dan upload ke Google Sheets.

## Cara Setup

### 1. Install dependencies
```bash
pip install pyzk gspread google-auth google-auth-oauthlib
```

### 2. Siapkan Environment Variables
```bash
export FINGERPRINT_IP="10.10.10.31"
export FINGERPRINT_PORT="4370"
export FINGERPRINT_PASSWORD="0"
export FINGERPRINT_UDP="false"
export SHEET_ID="your_google_sheet_id"
export WEB_APP_URL="your_apps_script_web_app_url"
```

### 3. Setup Google Apps Script
- Buat project di https://script.google.com/
- Deploy sebagai Web App (Anyone can access)
- Pastikan script mendukung `valueInputOption: 'RAW'` untuk format TEXT

### 4. Setup Cron (Linux)
```bash
# Setiap hari jam 09:00, 11:00, 20:00
0 9,11,20 * * * cd /path/to/app && /path/to/venv/bin/python3 fingerprint_pull.py
```

## Struktur Data

Kolom spreadsheet:
| NO | PIN | TANGGAL | JAM | STATUS | BULAN | TAHUN |
|----|-----|---------|-----|--------|-------|-------|

Semua kolom B-G dalam format **TEXT**.

## File

| File | Deskripsi |
|------|-----------|
| `fingerprint_pull.py` | Script utama pull & upload |
| `.env.example` | Contoh konfigurasi |
| `requirements.txt` | Python dependencies |
| `gas_webapp.js` | Google Apps Script (Web App) |
| `cron_setup.sh` | Setup cron job otomatis |
