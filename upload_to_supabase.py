#!/usr/bin/env python3
"""Upload room schedule data to Supabase"""

import json
import requests

SUPABASE_URL = "https://fgewwriulwdodmlbsotp.supabase.co"
SUPABASE_KEY = "sb_publishable_yvdyY62yUu7HgPw7wjy9XQ_jmcje9te"
SCHEDULE_FILE = "room_schedule_data.json"

def setup_tables():
    """Create tables via SQL"""
    setup_sql = """
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

    CREATE OR REPLACE FUNCTION normalize_booking_room(input_room TEXT)
    RETURNS TEXT
    LANGUAGE SQL
    IMMUTABLE
    AS $$
        SELECT CASE UPPER(BTRIM(input_room))
            WHEN 'MEETING ROOM' THEN 'B2036'
            WHEN 'TOEFL TESTING ICT LAB' THEN 'B1037'
            ELSE UPPER(BTRIM(input_room))
        END;
    $$;

    CREATE OR REPLACE FUNCTION prevent_booking_overlap()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    DECLARE
        new_room TEXT;
        new_date DATE;
        new_start TIME;
        new_end TIME;
        conflict_record RECORD;
    BEGIN
        new_room := normalize_booking_room(NEW.room);
        new_date := REPLACE(BTRIM(NEW.date), '/', '-')::DATE;
        new_start := BTRIM(NEW.start_time)::TIME;
        new_end := BTRIM(NEW.end_time)::TIME;

        PERFORM pg_advisory_xact_lock(hashtextextended(new_room || '|' || new_date::TEXT, 0));

        IF new_start >= new_end THEN
            RAISE EXCEPTION 'Booking end_time must be after start_time';
        END IF;

        SELECT src, room, date, start_time, end_time
        INTO conflict_record
        FROM (
            SELECT
                'bookings'::TEXT AS src,
                b.room,
                b.date,
                b.start_time,
                b.end_time
            FROM bookings b
            WHERE b.id IS DISTINCT FROM NEW.id
              AND normalize_booking_room(b.room) = new_room
              AND REPLACE(BTRIM(b.date), '/', '-')::DATE = new_date
              AND BTRIM(b.start_time)::TIME < new_end
              AND BTRIM(b.end_time)::TIME > new_start

            UNION ALL

            SELECT
                'room_sessions'::TEXT AS src,
                rs.room,
                rs.date,
                rs.start_time,
                rs.end_time
            FROM room_sessions rs
            WHERE normalize_booking_room(rs.room) = new_room
              AND REPLACE(BTRIM(rs.date), '/', '-')::DATE = new_date
              AND BTRIM(rs.start_time)::TIME < new_end
              AND BTRIM(rs.end_time)::TIME > new_start

            UNION ALL

            SELECT
                'schedule'::TEXT AS src,
                s.room,
                s.date,
                s.start_time,
                s.end_time
            FROM schedule s
            WHERE normalize_booking_room(s.room) = new_room
              AND REPLACE(BTRIM(s.date), '/', '-')::DATE = new_date
              AND BTRIM(s.start_time)::TIME < new_end
              AND BTRIM(s.end_time)::TIME > new_start
        ) conflicts
        LIMIT 1;

        IF FOUND THEN
            RAISE EXCEPTION 'Booking overlaps existing % entry for room % on % at %-%',
                conflict_record.src,
                new_room,
                TO_CHAR(new_date, 'YYYY-MM-DD'),
                conflict_record.start_time,
                conflict_record.end_time;
        END IF;

        NEW.room := new_room;
        NEW.date := TO_CHAR(new_date, 'YYYY/MM/DD');
        NEW.start_time := TO_CHAR(new_start, 'HH24:MI');
        NEW.end_time := TO_CHAR(new_end, 'HH24:MI');
        RETURN NEW;
    END;
    $$;

    DROP TRIGGER IF EXISTS bookings_prevent_overlap ON bookings;
    CREATE TRIGGER bookings_prevent_overlap
    BEFORE INSERT OR UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION prevent_booking_overlap();
    """

    print("Tables will be created via Supabase dashboard.")
    print("Please run these SQL statements in Supabase SQL Editor:")
    print("\n--- FULL SETUP SQL ---")
    print(setup_sql)

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