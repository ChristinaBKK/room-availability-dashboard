#!/usr/bin/env python3
"""Upload G9 B-building schedule data to Supabase"""

import json
import requests

SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SUPABASE_KEY = "sb_publishable_yvdyY62yUu7HgPw7wjy9XQ_jmcje9te"
SCHEDULE_FILE = "g9_b_schedule.json"

def upload_g9_schedule():
    """Upload G9 B-building schedule data to Supabase"""
    with open(SCHEDULE_FILE, 'r') as f:
        data = json.load(f)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "X-Client-Info": "matrix-agent"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/schedule"
    
    # Insert in batches
    batch_size = 100
    total = len(data)
    success = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = data[i:i+batch_size]
        records = []
        
        for item in batch:
            records.append({
                "date": item.get("date", ""),
                "start_time": item.get("start_time", ""),
                "end_time": item.get("end_time", ""),
                "class_name": item.get("class_name", ""),
                "room": item.get("room", ""),
                "teacher": item.get("teacher", "")
            })
        
        response = requests.post(url, json=records, headers=headers)
        
        if response.status_code in [200, 201]:
            success += len(records)
            print(f"Uploaded {min(i+batch_size, total)}/{total} records...")
        else:
            print(f"Error uploading batch: {response.status_code}")
            print(response.text[:200])
            failed += len(records)
    
    print(f"\nUpload complete! {success} G9 B-building records uploaded, {failed} failed.")
    return success

if __name__ == "__main__":
    upload_g9_schedule()
