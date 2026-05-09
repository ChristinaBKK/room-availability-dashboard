#!/usr/bin/env python3
"""Upload room schedule data to Supabase"""

import json
import requests

SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SUPABASE_KEY = "sb_publishable_yvdyY62yUu7HgPw7wjy9XQ_jmcje9te"
SCHEDULE_FILE = "room_schedule_data.json"

def setup_tables():
    """Create tables via SQL"""
    # Create schedule table
    schedule_sql = """
    CREATE TABLE IF NOT EXISTS schedule (
        id SERIAL PRIMARY KEY,
        date VARCHAR(20) NOT NULL,
        start_time VARCHAR(10) NOT NULL,
        end_time VARCHAR(10) NOT NULL,
        class_name VARCHAR(255),
        room VARCHAR(50) NOT NULL,
        teacher VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    # Create bookings table
    bookings_sql = """
    CREATE TABLE IF NOT EXISTS bookings (
        id SERIAL PRIMARY KEY,
        room VARCHAR(50) NOT NULL,
        date VARCHAR(20) NOT NULL,
        start_time VARCHAR(10) NOT NULL,
        end_time VARCHAR(10) NOT NULL,
        title VARCHAR(200),
        teacher VARCHAR(100),
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "X-Client-Info": "matrix-agent"
    }
    
    # Execute SQL via REST API
    # Note: For production, use Supabase SQL editor or pg admin
    
    print("Tables will be created via Supabase dashboard.")
    print("Please run these SQL statements in Supabase SQL Editor:")
    print("\n--- SCHEDULE TABLE ---")
    print(schedule_sql)
    print("\n--- BOOKINGS TABLE ---")
    print(bookings_sql)

def upload_schedule():
    """Upload schedule data to Supabase"""
    with open(SCHEDULE_FILE, 'r') as f:
        data = json.load(f)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "X-Client-Info": "matrix-agent"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/schedule"
    
    # Clear existing data first
    print("Clearing existing schedule data...")
    requests.delete(url, headers=headers)
    
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
                "date": item.get("Date", ""),
                "start_time": item.get("Start Time", ""),
                "end_time": item.get("End Time", ""),
                "class_name": item.get("Class", ""),
                "room": item.get("Room", ""),
                "teacher": item.get("Teacher", "")
            })
        
        response = requests.post(url, json=records, headers=headers)
        
        if response.status_code in [200, 201]:
            success += len(records)
            print(f"Uploaded {min(i+batch_size, total)}/{total} records...")
        else:
            print(f"Error uploading batch: {response.status_code}")
            print(response.text)
            failed += len(records)
    
    print(f"\nUpload complete! {success} records uploaded, {failed} failed.")

if __name__ == "__main__":
    setup_tables()
    print("\n" + "="*50)
    upload_schedule()