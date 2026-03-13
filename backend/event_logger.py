import sqlite3
from datetime import datetime


class EventLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS exam_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                score_deduction INTEGER DEFAULT 0,
                screenshot_frame TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                final_score INTEGER,
                trust_level TEXT
            )
        ''')

        # Seed demo students
        students = [
            ('STU001', 'Alice Johnson',    'pass123', 'alice@uni.edu'),
            ('STU002', 'Bob Smith',        'pass123', 'bob@uni.edu'),
            ('STU003', 'Carol Williams',   'pass123', 'carol@uni.edu'),
            ('ADMIN',  'Administrator',    'admin123', 'admin@uni.edu'),
        ]
        for sid, name, pwd, email in students:
            try:
                c.execute(
                    'INSERT INTO students (student_id, name, password, email) VALUES (?,?,?,?)',
                    (sid, name, pwd, email)
                )
            except sqlite3.IntegrityError:
                pass  # already exists

        conn.commit()
        conn.close()
        print("✅ Database initialized with demo students")

    def log(self, student_id: str, event_type: str, deduction: int, screenshot: str = ''):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            '''INSERT INTO exam_events
               (student_id, event_type, score_deduction, screenshot_frame, timestamp)
               VALUES (?, ?, ?, ?, ?)''',
            (student_id, event_type, deduction, screenshot, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
