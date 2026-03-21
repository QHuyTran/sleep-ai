import xml.etree.ElementTree as ET
import pandas as pd

print("Loading export.xml... this may take 30-60 seconds")
tree = ET.parse('export.xml')
root = tree.getroot()
print("Loaded successfully")

# Extract sleep data
sleep_records = []
for record in root.findall('Record'):
    if record.attrib.get('type') == 'HKCategoryTypeIdentifierSleepAnalysis':
        sleep_records.append({
            'start': record.attrib.get('startDate'),
            'end': record.attrib.get('endDate'),
            'value': record.attrib.get('value'),
            'source': record.attrib.get('sourceName')
        })

sleep_df = pd.DataFrame(sleep_records)

# Convert dates
sleep_df['start'] = pd.to_datetime(sleep_df['start'])
sleep_df['end'] = pd.to_datetime(sleep_df['end'])
sleep_df['duration_minutes'] = (
    sleep_df['end'] - sleep_df['start']).dt.total_seconds() / 60

# Keep only Apple Watch sources
apple_watch_sources = ["Quang Huy\u2019s Apple\xa0Watch",
                       "Apple\xa0Watch của Quang Huy"]
sleep_df = sleep_df[sleep_df['source'].isin(apple_watch_sources)].copy()

# Clean up stage names
sleep_df['stage'] = sleep_df['value'].str.replace(
    'HKCategoryValueSleepAnalysis', '')

# Assign date (use start date)
sleep_df['date'] = sleep_df['start'].dt.date

# Get unique dates
dates = sleep_df['date'].unique()

# Build daily summary manually
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

# Filter out incomplete tracking days
daily_sleep = daily_sleep[daily_sleep['total_sleep_hours'] > 2]

# Save
daily_sleep.to_csv('sleep_data.csv', index=False)
print(f"\nProcessed {len(daily_sleep)} nights of sleep data")
print(
    f"Date range: {daily_sleep['date'].min()} to {daily_sleep['date'].max()}")
print("\nLast 7 nights:")
print(daily_sleep.tail(7).to_string())
print("\nSaved to sleep_data.csv")
