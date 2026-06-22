# Changelog

## v2.0 - 2026-06-22

### Changed - Optimasi Pull Data
- **Sebelumnya**: Pull semua 63K+ records setiap kali cron jalan (~40 detik)
- **Sekarang**: Cek tanggal terakhir di spreadsheet, hanya pull data dari tanggal terakhir sampai hari ini

### Logika Baru
1. Cek `last_date` di spreadsheet via public CSV export
2. Pull semua attendance dari fingerprint device
3. Filter: skip data yang tanggalnya < `last_date`
4. Skip duplikat berdasarkan key (PIN, TANGGAL, JAM)
5. Upload hanya data baru

### Performa
- Pull 63K records: ~35 detik
- Filter by date: instant
- Upload: hanya data baru (biasanya < 100 rows per run)
- Total waktu per cron run: ~40 detik

### Contoh Output
```
Last date: 2026-06-22, Today: 2026-06-22
Pulled 63128, 31 new (63076 old skipped, 21 dup skipped)
Uploaded 31 rows
```

## v1.0 - 2026-06-21

### Initial Release
- Pull data fingerprint dari Solution X606-S via TCP/IP
- Upload ke Google Sheets via Apps Script Web App
- Cron job: jam 9, 11, 20 setiap hari
- Format kolom B-G: TEXT
- Anti-duplikat berdasarkan (PIN, TANGGAL, JAM)
