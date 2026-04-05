#!/bin/bash
# Weekly schedule sync from Google Sheets
# Add to crontab: 0 6 * * 1 /Users/elena/Developer/tennis_academy/scripts/weekly_sync.sh
# This runs every Monday at 6 AM

cd /Users/elena/Developer/tennis_academy
source venv/bin/activate 2>/dev/null || true
python3 scripts/sync_from_sheets.py >> /tmp/weekly_sync.log 2>&1

echo "$(date): Sync complete" >> /tmp/weekly_sync.log