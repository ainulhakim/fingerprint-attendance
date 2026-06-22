#!/usr/bin/env python3
"""
Fingerprint Attendance Auto-Pull
- Cek tanggal terakhir di spreadsheet
- Pull hanya data dari tanggal terakhir sampai hari ini
- Tidak ada duplikat
"""

from zk import ZK
import csv
import json
import urllib.request
import datetime
import os
import sys
import io
import time

# ===== CONFIG =====
FINGERPRINT_IP = '10.10.10.31'
FINGERPRINT_PORT = 4370
FINGERPRINT_PASSWORD = 0

SHEET_ID = 'YOUR_GOOGLE_SHEET_ID'
WEB_APP_URL = 'YOUR_APPS_SCRIPT_WEB_APP_URL'
# ==================

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(OUTPUT_DIR, 'cron.log')

def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def get_sheet_info():
    """Cek last_date, last_no, dan existing_keys dari spreadsheet"""
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode('utf-8')
    reader = csv.reader(io.StringIO(data))
    next(reader)
    existing_keys = set()
    last_no = 0
    last_date = None
    for r in reader:
        if len(r) >= 4:
            pin, tgl, jam = r[1].strip(), r[2].strip(), r[3].strip()
            parts = jam.split(':')
            if len(parts) == 3:
                jam = ':'.join(p.zfill(2) for p in parts)
            existing_keys.add((pin, tgl, jam))
            try:
                last_no = max(last_no, int(r[0]))
            except:
                pass
            if tgl and (last_date is None or tgl > last_date):
                last_date = tgl
    return last_date, last_no, existing_keys

def upload_batch(rows):
    data = json.dumps({'rows': rows}).encode('utf-8')
    req = urllib.request.Request(WEB_APP_URL, data=data, method='POST',
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())

def main():
    log('=== Cron: Fingerprint to Google Sheets ===')
    
    log('Checking spreadsheet for last date...')
    last_date, last_no, existing_keys = get_sheet_info()
    today = datetime.date.today().strftime('%Y-%m-%d')
    log(f'Last date: {last_date}, Today: {today}, Rows: {len(existing_keys)}')
    
    start_date = last_date if last_date else today
    
    # Connect
    conn = None
    for attempt in range(3):
        try:
            log(f'Connecting to {FINGERPRINT_IP}:{FINGERPRINT_PORT}...')
            zk = ZK(FINGERPRINT_IP, port=FINGERPRINT_PORT, timeout=120,
                    password=FINGERPRINT_PASSWORD, force_udp=False, ommit_ping=True)
            conn = zk.connect()
            log('Connected!')
            break
        except Exception as e:
            log(f'Error: {e}')
            if attempt < 2: time.sleep(10)
    
    if not conn:
        log('FAILED: Cannot connect')
        sys.exit(1)
    
    # Pull & filter
    log('Pulling attendance...')
    new_rows = []
    count = 0
    start_time = time.time()
    
    try:
        for att in conn.get_attendance():
            count += 1
            tanggal = att.timestamp.strftime('%Y-%m-%d')
            if tanggal < start_date:
                continue
            pin = str(att.user_id)
            jam = att.timestamp.strftime('%H:%M:%S')
            key = (pin, tanggal, jam)
            if key in existing_keys:
                continue
            last_no += 1
            bulan = tanggal.replace('-', '')[:6]
            new_rows.append([str(last_no), pin, tanggal, jam, str(att.status), bulan, bulan])
            existing_keys.add(key)
            if time.time() - start_time > 300:
                log('Timeout, stopping...')
                break
    except Exception as e:
        log(f'Pull error: {e}')
    
    log(f'Pulled {count}, {len(new_rows)} new')
    conn.disconnect()
    
    # Upload
    if new_rows:
        log(f'Uploading {len(new_rows)} rows...')
        total = 0
        for i in range(0, len(new_rows), 500):
            batch = new_rows[i:i+500]
            try:
                upload_batch(batch)
                total += len(batch)
            except Exception as e:
                log(f'Upload error: {e}')
                break
        log(f'Uploaded {total} rows')
    else:
        log('No new data')
    
    log('=== Complete ===')

if __name__ == '__main__':
    main()
