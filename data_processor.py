import xml.etree.ElementTree as ET
import pandas as pd
import zipfile
import io


def process_health_export(file_bytes):
    """
    Accepts raw bytes of either a zip file or xml file.
    Returns sleep_df, hrv_df, hr_df or raises an error.
    """
    # Handle zip file
    if zipfile.is_zipfile(io.BytesIO(file_bytes)):
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            # Find export.xml inside the zip
            xml_files = [f for f in z.namelist() if f.endswith('export.xml')]
            if not xml_files:
                raise ValueError(
                    "No export.xml found in zip file. Please export directly from Apple Health.")
            with z.open(xml_files[0]) as f:
                xml_bytes = f.read()
    else:
        xml_bytes = file_bytes

    # Parse XML
    root = ET.fromstring(xml_bytes.decode('utf-8'))

    # Extract sleep data
    sleep_records = []
    hrv_records = []
    hr_records = []

    for record in root.findall('Record'):
        record_type = record.attrib.get('type')
        source = record.attrib.get('sourceName', '')

        # Sleep
        if record_type == 'HKCategoryTypeIdentifierSleepAnalysis':
            sleep_records.append({
                'start': record.attrib.get('startDate'),
                'end': record.attrib.get('endDate'),
                'value': record.attrib.get('value'),
                'source': source
            })

        # HRV
        elif record_type == 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN':
            hrv_records.append({
                'date': record.attrib.get('startDate', '')[:10],
                'hrv': float(record.attrib.get('value', 0))
            })

        # Resting HR
        elif record_type == 'HKQuantityTypeIdentifierRestingHeartRate':
            hr_records.append({
                'date': record.attrib.get('startDate', '')[:10],
                'resting_hr': float(record.attrib.get('value', 0))
            })

    # Process sleep
    sleep_df = pd.DataFrame(sleep_records)
    if len(sleep_df) == 0:
        raise ValueError(
            "No sleep data found. Make sure you're uploading an Apple Health export.")

    sleep_df['start'] = pd.to_datetime(sleep_df['start'])
    sleep_df['end'] = pd.to_datetime(sleep_df['end'])
    sleep_df['duration_minutes'] = (
        sleep_df['end'] - sleep_df['start']).dt.total_seconds() / 60
    sleep_df['stage'] = sleep_df['value'].str.replace(
        'HKCategoryValueSleepAnalysis', '')
    sleep_df['date'] = sleep_df['start'].dt.date

    # Filter to Apple Watch sources - detect automatically
    watch_sources = [s for s in sleep_df['source'].unique()
                     if 'watch' in s.lower() or 'apple' in s.lower()]

    if watch_sources:
        sleep_df = sleep_df[sleep_df['source'].isin(watch_sources)].copy()

    # Build daily summary
    dates = sleep_df['date'].unique()
    rows = []
    for date in dates:
        day = sleep_df[sleep_df['date'] == date]
        asleep = day[day['stage'].isin(
            ['AsleepCore', 'AsleepREM', 'AsleepDeep', 'AsleepUnspecified'])]
        rem = day[day['stage'] == 'AsleepREM']
        deep = day[day['stage'] == 'AsleepDeep']
        core = day[day['stage'] == 'AsleepCore']
        awake = day[day['stage'] == 'Awake']

        rows.append({
            'date': date,
            'total_sleep_hours': asleep['duration_minutes'].sum() / 60,
            'rem_hours': rem['duration_minutes'].sum() / 60,
            'deep_hours': deep['duration_minutes'].sum() / 60,
            'core_hours': core['duration_minutes'].sum() / 60,
            'awake_minutes': awake['duration_minutes'].sum()
        })

    daily_sleep = pd.DataFrame(rows)
    daily_sleep = daily_sleep.sort_values('date').reset_index(drop=True)
    daily_sleep = daily_sleep[daily_sleep['total_sleep_hours'] > 2]
    daily_sleep['date'] = pd.to_datetime(daily_sleep['date'])

    # Process HRV
    if hrv_records:
        hrv_df = pd.DataFrame(hrv_records)
        hrv_df['date'] = pd.to_datetime(hrv_df['date'])
        hrv_df = hrv_df.groupby('date')['hrv'].mean().reset_index()
    else:
        hrv_df = pd.DataFrame(columns=['date', 'hrv'])

    # Process HR
    if hr_records:
        hr_df = pd.DataFrame(hr_records)
        hr_df['date'] = pd.to_datetime(hr_df['date'])
        hr_df = hr_df.groupby('date')['resting_hr'].mean().reset_index()
    else:
        hr_df = pd.DataFrame(columns=['date', 'resting_hr'])

    return daily_sleep, hrv_df, hr_df
