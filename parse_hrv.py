import xml.etree.ElementTree as ET
import pandas as pd

print("Loading export.xml...")
tree = ET.parse('export.xml')
root = tree.getroot()
print("Loaded successfully")

hrv_records = []
hr_records = []

for record in root.findall('Record'):
    record_type = record.attrib.get('type')

    if record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
        hrv_records.append({
            'date': record.attrib.get('startDate')[:10],
            'hrv': float(record.attrib.get('value'))
        })

    if record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
        hr_records.append({
            'date': record.attrib.get('startDate')[:10],
            'resting_hr': float(record.attrib.get('value'))
        })

# HRV - daily average
hrv_df = pd.DataFrame(hrv_records)
if len(hrv_df) > 0:
    hrv_df['date'] = pd.to_datetime(hrv_df['date']).dt.date
    hrv_daily = hrv_df.groupby('date')['hrv'].mean().reset_index()
    hrv_daily.to_csv('hrv_data.csv', index=False)
    print(f"\nHRV records: {len(hrv_daily)} days")
    print(hrv_daily.tail(7).to_string())
else:
    print("No HRV data found")

# Resting HR - daily
hr_df = pd.DataFrame(hr_records)
if len(hr_df) > 0:
    hr_df['date'] = pd.to_datetime(hr_df['date']).dt.date
    hr_daily = hr_df.groupby('date')['resting_hr'].mean().reset_index()
    hr_daily.to_csv('heart_rate.csv', index=False)
    print(f"\nResting HR records: {len(hr_daily)} days")
    print(hr_daily.tail(7).to_string())
else:
    print("No resting HR data found")
