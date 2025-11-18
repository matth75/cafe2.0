import pandas as pd
import sqlite3
import os

# --- CONFIGURATION ---
csv_file = "test_calendar_for_ics.xls"          # path to your .ods file
table_name = "events"         # must already exist in the SQLite DB
sqlite_db = "webcafe.db"    # your SQLite database file

# Vérifier si le fichier existe
if not os.path.exists(csv_file):
    raise FileNotFoundError(f"Le fichier {csv_file} n'a pas été trouvé.")

# --- LIRE LE FICHIER CSV ---
df = pd.read_excel(csv_file)

# --- CONNECT TO SQLITE ---
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

# --- INSERT INTO EXISTING TABLE ---
# Make sure column names in ODS match the table's column names
df.to_sql(table_name, conn, if_exists='append', index=False)

# --- CLEANUP ---
conn.commit()
conn.close()

print(f"Data from {csv_file} inserted into table '{table_name}' in {sqlite_db}")
