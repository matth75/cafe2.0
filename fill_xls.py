import pandas as pd
from datetime import datetime, timedelta


#### script to add all dates to the excel file to improve manual events input


# Path to your Excel file
file_path = 'all_events.xlsx'  # Replace with your actual file path
output_path = 'all_events.xlsx'  # Output path for the filled file

# Load the existing Excel file
df = pd.DataFrame()

# Get the current date and time
current_time = datetime.now()

# Define the end date (December 31st)
end_date = datetime(2025, 12, 22, 23, 59)

# Initialize the start date for the first row
start_time = datetime(2025, 11, 18, 8, 0)
start_time_afternoon = datetime(2025, 11, 18, 13, 30)

# Create lists to hold the start and end times
start_times = []
end_times = []



# Loop until we reach the end date
while start_time <= end_date:
    # Append the start and end times to the lists
    start_times.append(start_time.strftime('%Y-%m-%dT%H:%M'))
    end_times.append((start_time + timedelta(hours=4, minutes=15)).strftime('%Y-%m-%dT%H:%M'))
    start_times.append(start_time_afternoon.strftime('%Y-%m-%dT%H:%M'))
    end_times.append((start_time_afternoon + timedelta(hours=4, minutes=15)).strftime('%Y-%m-%dT%H:%M'))
    # Move to the next time slot (24 hours increment)
    start_time += timedelta(days=1)
    start_time_afternoon += timedelta(days=1)

# Add the new times to the dataframe
df['start'] = start_times 
df['end'] = end_times

# Save the updated dataframe to a new Excel file
df.to_excel(output_path, index=False)

print(f"Excel file with updated start and end times saved to {output_path}")
