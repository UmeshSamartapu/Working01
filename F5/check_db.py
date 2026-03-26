#!/usr/bin/env python
import sqlite3
import os

db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get last 15 records
    cursor.execute('SELECT id, result, heart_image FROM UserApp_ecgrecord ORDER BY id DESC LIMIT 15')
    rows = cursor.fetchall()
    
    print("=" * 100)
    print(f"Total records to display: {len(rows)}")
    print("=" * 100)
    
    for r in rows:
        record_id, result, heart_image = r
        print(f"\nID: {record_id}")
        print(f"Result: {result[:60]}")
        print(f"Heart Image: {heart_image}")
        
        # Check if image file exists
        if heart_image:
            media_path = os.path.join('media', heart_image)
            exists = os.path.exists(media_path)
            print(f"File exists: {exists} (path: {media_path})")
    
    conn.close()
else:
    print(f"Database not found: {db_path}")
