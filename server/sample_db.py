import sqlite3
import csv

def start_db(file_path='samples/policy_info.csv'):
    # Create a new SQLite database in memory
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()

    # Create table schema
    cur.execute('''
    CREATE TABLE insurance_policy (
        patient_id INTEGER PRIMARY KEY,
        patient_name TEXT,
        policy_no TEXT,
        claim_limit INTEGER,
        policy_start_date TEXT,
        policy_end_date TEXT,
        active TEXT
    )
    ''')

    # Read data from CSV file and insert into the table
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            cur.execute('INSERT INTO insurance_policy VALUES (?, ?, ?, ?, ?, ?, ?)', row)



    # Commit the changes
    conn.commit()
    return cur
    
