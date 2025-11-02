import sqlite3
def create_seat_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seat_availability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number TEXT,
            train_name TEXT,
            source TEXT,
            destination TEXT,
            date_of_journey TEXT,
            class_type TEXT,
            total_seats INTEGER,
            available_seats INTEGER
        )
    """)
    conn.commit()

    # Insert sample data if empty
    cursor.execute("SELECT COUNT(*) FROM seat_availability")
    if cursor.fetchone()[0] == 0:
        sample_seats = [
            ("12627", "Karnataka Express", "Delhi", "Bangalore", "2025-11-05", "Sleeper", 200, 35),
            ("12627", "Karnataka Express", "Delhi", "Bangalore", "2025-11-05", "3A", 72, 12),
            ("12841", "Coromandel Express", "Kolkata", "Chennai", "2025-11-06", "2A", 48, 6),
            ("12951", "Mumbai Rajdhani", "Mumbai", "Delhi", "2025-11-07", "1A", 22, 2),
            ("12723", "Andhra Express", "Vijayawada", "Delhi", "2025-11-08", "Sleeper", 180, 20),
            ("12659", "Chennai Mail", "Chennai", "Delhi", "2025-11-09", "3A", 72, 10),
            ("12760", "Charminar Express", "Hyderabad", "Chennai", "2025-11-10", "Sleeper", 200, 42),
            ("12009", "Shatabdi Express", "Bhopal", "Delhi", "2025-11-11", "Chair Car", 100, 18),
            ("16382", "Kanniyakumari Express", "Trivandrum", "Mumbai", "2025-11-12", "Sleeper", 220, 8),
            ("12533", "Pushpak Express", "Lucknow", "Mumbai", "2025-11-13", "2A", 52, 9),
        ]

        cursor.executemany("""
            INSERT INTO seat_availability (
                train_number, train_name, source, destination,
                date_of_journey, class_type, total_seats, available_seats
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_seats)
        conn.commit()
        print("✅ Seat Availability table created with 10 sample records.")
    else:
        print("ℹ️ Seat Availability table already exists, skipping data insertion.")


def get_seat_availability(conn: sqlite3.Connection, train_number: str, date_of_journey: str, class_type: str):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM seat_availability 
        WHERE train_number = ? AND date_of_journey = ? AND class_type = ?
    """, (train_number, date_of_journey, class_type))
    result = cursor.fetchone()
    if result:
        keys = [
            "id", "train_number", "train_name", "source", "destination",
            "date_of_journey", "class_type", "total_seats", "available_seats"
        ]
        return dict(zip(keys, result))
    else:
        return None