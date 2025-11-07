import pandas as pd
import sqlite3

# --- CONFIGURATION ---
ods_file = "backend/fill_events.ods"          # path to your .ods file
table_name = "events"         # must already exist in the SQLite DB
sqlite_db = "webcafe.db"    # your SQLite database file

# --- READ THE ODS FILE ---
# engine="odf" is required for .ods files
df = pd.read_excel(ods_file, engine="odf")

# --- CONNECT TO SQLITE ---
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

# --- INSERT INTO EXISTING TABLE ---
# Make sure column names in ODS match the table's column names
df.to_sql(table_name, conn, if_exists='append', index=False)

# --- CLEANUP ---
conn.commit()
conn.close()

print(f"Data from {ods_file} inserted into table '{table_name}' in {sqlite_db}")
