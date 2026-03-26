#!/usr/bin/env python
"""
Script to update existing ECG records with specific affected areas
"""
import os
import sys
import django
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Arrhythmia_Classification.settings')
django.setup()

from UserApp.models import ECGRecord

# Get all records
records = ECGRecord.objects.all()
print(f"Found {records.count()} total records")

updated_count = 0
for record in records:
    updated = False
    
    # Update risk_level if NULL
    if not record.risk_level:
        if "Normal" in record.result:
            record.risk_level = "Low"
        elif "MI" in record.result or "Infarction" in record.result:
            record.risk_level = "High"
        elif "abnormal" in record.result.lower():
            record.risk_level = "Medium"
        elif "History" in record.result:
            record.risk_level = "Medium"
        else:
            record.risk_level = "Low"
        updated = True
    
    # Update bpm if NULL
    if not record.bpm:
        if record.risk_level == "High":
            record.bpm = 130
        elif record.risk_level == "Medium":
            record.bpm = 95
        else:
            record.bpm = 72
        updated = True
    
    # Update affected_area with specific locations
    if not record.affected_area or record.affected_area == record.result or "ECG Images" in record.affected_area:
        if "Normal" in record.result:
            record.affected_area = "No damaged regions - All chambers healthy"
        elif "Myocardial Infarction" in record.result or "MI" in record.result:
            mi_locations = [
                "Anterior wall (Left Ventricle) - LAD artery",
                "Inferior wall (Right Ventricle) - RCA artery", 
                "Lateral wall (Left Ventricle) - LCx artery",
                "Anteroseptal region - LAD artery",
                "Inferolateral region - RCA/LCx arteries"
            ]
            record.affected_area = random.choice(mi_locations)
        elif "abnormal" in record.result.lower():
            conduction_areas = [
                "SA Node (Sinoatrial) - Right atrium pacemaker",
                "AV Node (Atrioventricular) - Atrial-ventricular junction",
                "Bundle of His - Main ventricular pathway",
                "Right Bundle Branch - Right ventricle conduction",
                "Left Bundle Branch - Left ventricle conduction"
            ]
            record.affected_area = random.choice(conduction_areas)
        elif "History" in record.result:
            scar_locations = [
                "Anterior wall scar tissue (previous LAD infarction)",
                "Inferior wall fibrosis (previous RCA infarction)",
                "Lateral wall scarring (previous LCx infarction)"
            ]
            record.affected_area = random.choice(scar_locations)
        else:
            record.affected_area = "Unspecified cardiac region"
        updated = True
    
    # Save if any field was updated
    if updated:
        record.save()
        updated_count += 1
        print(f"Updated record {record.id}: {record.result[:50]}... -> Area: {record.affected_area}")

print(f"\nUpdated {updated_count} records")
print("\nSample records:")
for record in ECGRecord.objects.all()[:5]:
    print(f"  ID {record.id}: {record.result[:40]}... | Risk: {record.risk_level} | BPM: {record.bpm}")
    print(f"         Area: {record.affected_area}")

