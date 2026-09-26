import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'personal_ai.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Tasks Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            priority TEXT DEFAULT 'Medium',
            status TEXT DEFAULT 'pending',
            estimated_minutes INTEGER DEFAULT 30,
            notes TEXT,
            source TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Schedule Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            location TEXT,
            items_to_take TEXT,
            date_str TEXT DEFAULT 'Today'
        )
    ''')

    # Calendar Events & Birthday Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_type TEXT DEFAULT 'Event', -- 'Birthday', 'Exam', 'Event'
            event_date TEXT NOT NULL,
            reminder_days_before INTEGER DEFAULT 30,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Documents & Notes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'Note',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Zara Self-Learned Memory & Behavioral Preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zara_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL, -- 'Routine', 'Food Preference', 'Habit', 'Goal'
            fact TEXT NOT NULL,
            confidence_level REAL DEFAULT 1.0,
            learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # User Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    # Seed Events if empty
    cursor.execute('SELECT COUNT(*) FROM events')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO events (title, event_type, event_date, reminder_days_before, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ("Rahul's Birthday 🎂", 'Birthday', '2026-10-14', 30, 'Buy a gift and send birthday wishes!'),
            ('Data Structures Midterm Exam 📝', 'Exam', '2026-10-20', 14, 'Covers BSTs, AVL Trees, Graphs, and Sorting Algorithms.')
        ])

    # Seed Zara Memory if empty
    cursor.execute('SELECT COUNT(*) FROM zara_memory')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO zara_memory (category, fact, confidence_level)
            VALUES (?, ?, ?)
        ''', [
            ('Routine', 'Prefers studying in the evening between 6:00 PM and 9:00 PM', 0.95),
            ('Food Preference', 'Enjoys eating Biryani and drinking cold coffee while studying', 0.90),
            ('Habit', 'Tends to scroll reels when taking breaks; benefits from gentle study reminders', 0.88),
            ('Companion Goal', 'Aspires to excel in Computer Science while maintaining balance', 0.98)
        ])

    # Default Seed Settings
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('assistant_name', 'Zara')")
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('user_name', 'Mayur')")
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('tone', 'friendly')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized with Calendar & Zara Self-Learning Memory!")
