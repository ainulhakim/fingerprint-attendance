#!/usr/bin/env python3
"""
Fingerprint Attendance Auto-Pull
Pull data dari fingerprint device dan upload ke Google Sheets
"""

from zk import ZK
import csv
import json
import urllib.request
import urllib.parse
import datetime
import os
import sys
import io

# ============ CONFIG ============
# Semua config via environment variable atau .env file
FINGERPRINT_IP = os.environ.get('FINGERPRINT_IP', '10.10.10.31')
FINGERPRINT_PORT = int(os.environ.get('FINGERPRINT_PORT', '4370'))
FINGERPRINT_PASSWORD = int(os.environ.get('FINGERPRINT_PASSWORD', '0'))
FINGERPRINT_UDP = os.environ.get('FINGERPRINT_UDP', 'false').lower() == 'true'

SHEET_ID = os.environ.get('SHEET_ID', 'YOUR_GOOGLE_SHEET_ID')
WEB_APP_URL = os.environ.get('WEB_APP_URL', 'YOUR_APPS_SCRIPT_WEB_APP_URL')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(OUTPUT_DIR, 'cron.log')
# ================================


def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def get_existing_keys():
    """Get existing (PIN, TANGGAL, JAM) dari Google Sheets via public CSV export"""
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode('utf-8')

    reader = csv.reader(io.StringIO(data))
    next(reader)  # skip header

    keys = set()
    last_no = 0
    for r in reader:
        if len(r) >= 4:
            pin = r[1].strip()
            tgl = r[2].strip()
            jam = r[3].strip()
            parts = jam.split(':')
            if len(parts) == 3:
                jam = ':'.join(p.zfill(2) for p in parts)
            keys.add((pin, tgl, jam))
            try:
                last_no = max(last_no, int(r[0]))
            except (ValueError, IndexError):
                pass

    return keys, last_no


def upload_batch(rows):
    """Upload rows ke Google Sheets via Apps Script Web App"""
    data = json.dumps({'rows': rows}).encode('utf-8')
    req = urllib.request.Request(
        WEB_APP_URL, data=data, method='POST',
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def connect_fingerprint():
    """Connect ke fingerprint device"""
    zk = ZK(
        FINGERPRINT_IP,
        port=FINGERPRINT_PORT,
        timeout=60,
        password=FINGERPRINT_PASSWORD,
        force_udp=FINGERPRINT_UDP,
        ommit_ping=False
    )
    return zk.connect()


def main():
    log('=== Fingerprint Attendance Auto-Pull ===')

    # Get existing sheet data
    log('Fetching existing sheet data...')
    existing_keys, last_no = get_existing_keys()
    log(f'Existing rows: {len(existing_keys)}, Last NO: {last_no}')

    # Connect to fingerprint
    log(f'Connecting to {FINGERPRINT_IP}:{FINGERPRINT_PORT}...')

    import time
    retry = 0
    max_retries = 3
    conn = None

    while retry < max_retries:
        try:
            conn = connect_fingerprint()
            log('Connected!')
            break
        except Exception as e:
            retry += 1
            log(f'Connection error (attempt {retry}/{max_retries}): {e}')
            if retry < max_retries:
                time.sleep(10)

    if not conn:
        log('FAILED: Cannot connect to fingerprint device')
        sys.exit(1)

    # Get users
    users = conn.get_users()
    user_map = {u.uid: u.name for u in users}

    # Pull attendance & filter new
    log('Pulling attendance...')
    new_rows = []
    count = 0

    for att in conn.get_attendance():
        count += 1
        pin = str(att.user_id)
        tanggal = att.timestamp.strftime('%Y-%m-%d')
        jam = att.timestamp.strftime('%H:%M:%S')
        status = str(att.status)

        key = (pin, tanggal, jam)
        if key not in existing_keys:
            last_no += 1
            bulan = tanggal.replace('-', '')[:6]
            new_rows.append([str(last_no), pin, tanggal, jam, status, bulan, bulan])
            existing_keys.add(key)

    log(f'Pulled {count} records, {len(new_rows)} new')
    conn.disconnect()

    # Upload
    if new_rows:
        log(f'Uploading {len(new_rows)} new rows...')
        BATCH_SIZE = 500
        total_uploaded = 0

        for i in range(0, len(new_rows), BATCH_SIZE):
            batch = new_rows[i:i + BATCH_SIZE]
            try:
                result = upload_batch(batch)
                total_uploaded += len(batch)
                log(f'  Uploaded {total_uploaded}/{len(new_rows)}')
            except Exception as e:
                log(f'  Upload error: {e}')
                break

        log(f'Done! Uploaded {total_uploaded} new rows')
    else:
        log('No new data to upload')

    log('=== Complete ===')


if __name__ == '__main__':
    main()
