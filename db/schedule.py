import sqlite3
def create_train_schedule_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS train_schedule (
            train_number TEXT PRIMARY KEY,
            train_name TEXT,
            source TEXT,
            destination TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            travel_duration TEXT,
            days_of_operation TEXT
        )
    """)
    conn.commit()

    # Insert sample train schedules if table is empty
    cursor.execute("SELECT COUNT(*) FROM train_schedule")
    if cursor.fetchone()[0] == 0:
        sample_schedules = [
            ("12627", "Karnataka Express", "New Delhi", "Bangalore", "20:20", "08:10", "35h 50m", "Daily"),
            ("12841", "Coromandel Express", "Kolkata", "Chennai", "14:50", "18:45", "27h 55m", "Daily"),
            ("12951", "Mumbai Rajdhani", "Mumbai Central", "New Delhi", "17:00", "08:35", "15h 35m", "Daily"),
            ("12723", "Andhra Express", "Vijayawada", "New Delhi", "05:25", "11:00", "29h 35m", "Daily"),
            ("12659", "Chennai Mail", "Chennai Central", "New Delhi", "23:00", "06:30", "31h 30m", "Daily"),
            ("12760", "Charminar Express", "Hyderabad", "Chennai", "18:00", "07:50", "13h 50m", "Daily"),
            ("12009", "Shatabdi Express", "Bhopal", "New Delhi", "06:00", "12:00", "6h 00m", "Daily"),
            ("16382", "Kanniyakumari Express", "Trivandrum", "Mumbai", "05:20", "22:15", "16h 55m", "Mon, Wed, Fri"),
            ("12533", "Pushpak Express", "Lucknow", "Mumbai CST", "20:30", "16:10", "19h 40m", "Daily"),
            ("12615", "Grand Trunk Express", "New Delhi", "Chennai", "18:40", "05:30", "34h 50m", "Daily"),
        ]

        cursor.executemany("""
            INSERT INTO train_schedule (
                train_number, train_name, source, destination,
                departure_time, arrival_time, travel_duration, days_of_operation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_schedules)
        conn.commit()
        print("✅ Train Schedule table created with 10 sample records.")
    else:
        print("ℹ️ Train Schedule table already exists, skipping data insertion.")
def get_train_schedule(conn: sqlite3.Connection, train_number: str):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM train_schedule WHERE train_number = ?", (train_number,))
    result = cursor.fetchone()
    if result:
        keys = [
            "train_number", "train_name", "source", "destination",
            "departure_time", "arrival_time", "travel_duration", "days_of_operation"
        ]
        return dict(zip(keys, result))
    else:
        return None