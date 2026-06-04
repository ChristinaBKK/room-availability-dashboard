#!/usr/bin/env python3
"""Upload G9 B-building schedule data to Supabase"""

import json
import os
import requests

DEFAULT_SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SCHEDULE_FILE = "g9_b_schedule.json"
CLASS_NAME_ALIASES = {
    "ADVANCED MATH C (CIE)": "Advanced Maths (CIE) C",
}


def get_supabase_config() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    supabase_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
    )
    if not supabase_key:
        raise RuntimeError(
            "Missing Supabase API key. Set SUPABASE_SERVICE_ROLE_KEY, SERVICE_ROLE_KEY, SUPABASE_KEY, or SUPABASE_ANON_KEY."
        )
    return supabase_url, supabase_key


def normalize_class_name(value: str) -> str:
    class_name = (value or "").strip()
    if not class_name:
        return ""
    return CLASS_NAME_ALIASES.get(class_name.upper(), class_name)

def upload_g9_schedule():
    """Upload G9 B-building schedule data to Supabase"""
    supabase_url, supabase_key = get_supabase_config()
    with open(SCHEDULE_FILE, 'r') as f:
        data = json.load(f)
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "X-Client-Info": "matrix-agent"
    }
    
    url = f"{supabase_url}/rest/v1/schedule"
    
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
                "class_name": normalize_class_name(item.get("class_name", "")),
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
