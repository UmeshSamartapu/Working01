import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Arrhythmia_Classification.settings')
django.setup()

from UserApp.models import ECGRecord

print("\n" + "="*120)
print("ECG RECORD DATABASE CHECK")
print("="*120)

records = ECGRecord.objects.all().order_by('-id')[:15]
print(f"\nTotal records in database: {ECGRecord.objects.count()}")
print(f"Showing last 15 records:\n")

for idx, record in enumerate(records, 1):
    print(f"\n[{idx}] Record ID: {record.id}")
    print(f"    Result: {record.result[:60]}")
    print(f"    Heart Image Field: {record.heart_image}")
    print(f"    Heart Image Name: {record.heart_image.name if record.heart_image else 'EMPTY'}")
    print(f"    Heart Image URL: {record.heart_image.url if record.heart_image else 'NO URL'}")
    
    # Check if file exists
    if record.heart_image:
        full_path = record.heart_image.path
        file_exists = os.path.exists(full_path)
        file_size = os.path.getsize(full_path) if file_exists else 0
        print(f"    Full Path: {full_path}")
        print(f"    File Exists: {file_exists}")
        print(f"    File Size: {file_size} bytes")
    else:
        print(f"    ⚠️ NO HEART IMAGE DATA STORED")

print("\n" + "="*120)
print("END OF REPORT")
print("="*120 + "\n")
