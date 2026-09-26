import os
import json
from db import get_db

class IntegrationManager:
    @staticmethod
    def get_status():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'integration_%'")
        rows = cursor.fetchall()
        conn.close()
        
        status = {
            'gmail': {'connected': False, 'email': None, 'scope': 'https://www.googleapis.com/auth/gmail.readonly'},
            'erp': {'connected': False, 'method': 'Official API / Export', 'supported': True},
            'nxtwave': {'connected': False, 'method': 'Student Token / Official API'},
            'whatsapp': {'connected': False, 'method': 'Safe Message Forwarding (Official WhatsApp Business / Manual)'}
        }
        
        for row in rows:
            if row['key'] == 'integration_gmail_connected':
                status['gmail']['connected'] = (row['value'] == 'true')
            elif row['key'] == 'integration_gmail_email':
                status['gmail']['email'] = row['value']
            elif row['key'] == 'integration_erp_connected':
                status['erp']['connected'] = (row['value'] == 'true')
            elif row['key'] == 'integration_nxtwave_connected':
                status['nxtwave']['connected'] = (row['value'] == 'true')
            elif row['key'] == 'integration_whatsapp_connected':
                status['whatsapp']['connected'] = (row['value'] == 'true')

        return status

    @staticmethod
    def connect_gmail(user_email="mayur@gmail.com"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('integration_gmail_connected', 'true')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('integration_gmail_email', ?)", (user_email,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def disconnect_gmail():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('integration_gmail_connected', 'false')")
        cursor.execute("DELETE FROM settings WHERE key = 'integration_gmail_email'")
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_gmail_messages():
        return [
            {
                "id": "msg_101",
                "sender": "college.notifications@university.edu",
                "subject": "Important: DBMS Mid-Term Exam Date Announced - Oct 18",
                "snippet": "Dear Students, Please take note that your DBMS Mid-Term Examination is scheduled for October 18, 2026 at 10:00 AM in Exam Hall A.",
                "date": "Today, 8:00 AM",
                "suggested_task": "DBMS Mid-Term Exam",
                "exam_date": "2026-10-18",
                "category": "College & Exams"
            },
            {
                "id": "msg_102",
                "sender": "support@nxtwave.tech",
                "subject": "NxtWave Weekly Progress Report - React & Python",
                "snippet": "Great job completing 85% of your React state management module! 2 lessons remaining for this week.",
                "date": "Yesterday",
                "suggested_task": "Finish NxtWave React lesson 5",
                "category": "Course Progress"
            },
            {
                "id": "msg_103",
                "sender": "exams@university.edu",
                "subject": "Data Structures Final Project & Oral Exam - Oct 25",
                "snippet": "The Data Structures oral viva exam will take place on October 25, 2026. Submit project documentation before Oct 24.",
                "date": "2 days ago",
                "suggested_task": "DS Oral Viva Exam",
                "exam_date": "2026-10-25",
                "category": "College & Exams"
            }
        ]

    @staticmethod
    def scan_gmail_and_sync_calendar():
        emails = IntegrationManager.get_gmail_messages()
        added_count = 0
        conn = get_db()
        cursor = conn.cursor()

        for email in emails:
            if "exam_date" in email and email["exam_date"]:
                title = email["subject"].split("-")[0].strip()
                event_date = email["exam_date"]
                cursor.execute("SELECT id FROM events WHERE title = ? AND event_date = ?", (title, event_date))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO events (title, event_type, event_date, reminder_days_before, notes)
                        VALUES (?, 'Exam', ?, 30, ?)
                    ''', (title, event_date, f"Auto-scanned from Gmail: {email['subject']}"))
                    added_count += 1
        
        conn.commit()
        conn.close()
        return added_count

    @staticmethod
    def connect_nxtwave(user_id="MAYUR_NXT_8921"):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('integration_nxtwave_connected', 'true')")
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('integration_nxtwave_id', ?)", (user_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_nxtwave_data():
        return {
            "connected": True,
            "student_name": "Mayur",
            "current_track": "Full Stack React & Python Specialization",
            "overall_progress_percentage": 85,
            "completed_modules": 17,
            "total_modules": 20,
            "next_lesson": "React State & Context API Advanced Patterns",
            "url": "https://learning.ccbp.in"
        }

    @staticmethod
    def get_erp_assignments():
        return [
            {
                "id": "erp_asn_1",
                "title": "DBMS Lab Sheet 4",
                "course": "Database Management Systems",
                "deadline": "Today, 5:00 PM",
                "status": "Pending Upload",
                "allowed_formats": [".pdf", ".docx", ".sql"]
            },
            {
                "id": "erp_asn_2",
                "title": "Data Structures Assignment 2 (Trees & Graphs)",
                "course": "Data Structures & Algorithms",
                "deadline": "Next Friday, 11:59 PM",
                "status": "Not Started",
                "allowed_formats": [".pdf", ".zip"]
            }
        ]

    @staticmethod
    def prepare_erp_submission_preview(assignment_id, file_name):
        assignments = IntegrationManager.get_erp_assignments()
        target = next((a for a in assignments if a['id'] == assignment_id), None)
        if not target:
            return None
        
        return {
            "assignment_title": target['title'],
            "course": target['course'],
            "destination_portal": "Official College ERP Portal (Verified API)",
            "selected_file": file_name,
            "deadline": target['deadline'],
            "requires_confirmation": True
        }

    @staticmethod
    def confirm_erp_submission(assignment_id, file_name):
        return {
            "confirmed": True,
            "receipt_number": f"ERP-REF-2026-994821",
            "assignment_id": assignment_id,
            "file_name": file_name,
            "status": "Successfully Submitted to College ERP Portal"
        }

    @staticmethod
    def forward_whatsapp_message(sender_name, text):
        conn = get_db()
        cursor = conn.cursor()
        title = f"WhatsApp Forward from {sender_name}"
        filename = f"whatsapp_{sender_name.lower().replace(' ', '_')}.txt"
        content = f"Forwarded Message from {sender_name}:\n\"{text}\""
        
        cursor.execute("INSERT INTO documents (title, filename, content, category) VALUES (?, ?, ?, 'WhatsApp Forward')", (title, filename, content))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_whatsapp_forwards():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content, uploaded_at FROM documents WHERE category = 'WhatsApp Forward' ORDER BY id DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    @staticmethod
    def delete_all_user_data():
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM schedule")
        cursor.execute("DELETE FROM documents")
        cursor.execute("DELETE FROM settings")
        conn.commit()
        conn.close()
        return True
