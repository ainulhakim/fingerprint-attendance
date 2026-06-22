#!/bin/bash
# Setup cron job untuk fingerprint auto-pull
# Jalankan: bash cron_setup.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH="/usr/bin/python3"
CRON_SCHEDULE="0 9,11,20 * * *"

# Check if venv exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
fi

CRON_CMD="$CRON_SCHEDULE cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_DIR/fingerprint_pull.py"

# Add to crontab (remove old entry first)
(crontab -l 2>/dev/null | grep -v 'fingerprint_pull'; echo "$CRON_CMD") | crontab -

echo "Cron job installed:"
crontab -l | grep fingerprint_pull
