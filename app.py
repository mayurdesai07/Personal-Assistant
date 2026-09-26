import os
import json
from flask import Flask, render_template, request, jsonify
from db import init_db, get_db
from assistant_engine import process_user_query, check_duplicate_task, parse_quick_capture
from integrations import IntegrationManager
from system_control import SystemControl

app = Flask(__name__)

# Initialize database tables
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# ---------------------------------------------------------------------------
# API: Laptop System Admin Control & App Execution
# ---------------------------------------------------------------------------
@app.route('/api/system/stats', methods=['GET'])
def get_system_stats():
    stats = SystemControl.get_system_stats()
    return jsonify({"status": "success", "stats": stats})

@app.route('/api/system/launch', methods=['POST'])
def launch_laptop_app():
    data = request.json or {}
    app_name = data.get('app_name', 'notepad')
    res = SystemControl.launch_application(app_name)
    return jsonify({"status": "success", "message": res})

# ---------------------------------------------------------------------------
# API: Calendar Events & Birthday Reminders
# ---------------------------------------------------------------------------
@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
    events = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "events": events})

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json or {}
    title = data.get('title', '').strip()
    event_type = data.get('event_type', 'Event')
    event_date = data.get('event_date', '2026-10-14').strip()
    reminder_days = data.get('reminder_days_before', 30)
    notes = data.get('notes', '')

    if not title or not event_date:
        return jsonify({"status": "error", "message": "Title and event date are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (title, event_type, event_date, reminder_days_before, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, event_type, event_date, reminder_days, notes))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "Event added to Zara's Calendar", "event_id": event_id})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Event deleted"})

# ---------------------------------------------------------------------------
# API: Zara Self-Learned Companion Memory
# ---------------------------------------------------------------------------
@app.route('/api/memory', methods=['GET'])
def get_memory():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM zara_memory ORDER BY id DESC")
    memories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "memories": memories})

@app.route('/api/memory', methods=['POST'])
def add_memory():
    data = request.json or {}
    category = data.get('category', 'Habit')
    fact = data.get('fact', '').strip()

    if not fact:
        return jsonify({"status": "error", "message": "Fact is required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO zara_memory (category, fact, confidence_level) VALUES (?, ?, 0.95)", (category, fact))
    conn.commit()
    mem_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "Fact learned by Zara!", "memory_id": mem_id})

# ---------------------------------------------------------------------------
# API: Quick Capture Analyzer & Confirmation
# ---------------------------------------------------------------------------
@app.route('/api/quick-capture/parse', methods=['POST'])
def quick_capture_parse():
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"status": "error", "message": "Empty capture text"}), 400

    parsed = parse_quick_capture(text)
    return jsonify({"status": "success", "parsed": parsed})

@app.route('/api/quick-capture/save', methods=['POST'])
def quick_capture_save():
    data = request.json or {}
    category = data.get('category', 'Task')
    title = data.get('title', '').strip()
    time_str = data.get('suggested_time', 'Today')
    checklist = data.get('checklist_items', [])

    if not title:
        return jsonify({"status": "error", "message": "Title is required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    if category == "Appointment / Class":
        cursor.execute('''
            INSERT INTO schedule (title, time_slot, location, items_to_take, date_str)
            VALUES (?, ?, 'Assigned via Quick Capture', ?, ?)
        ''', (title, time_str, json.dumps(checklist), 'Today'))
    else:
        cursor.execute('''
            INSERT INTO tasks (title, due_date, priority, status, estimated_minutes, notes, source)
            VALUES (?, ?, 'High', 'pending', 30, ?, 'Quick Capture')
        ''', (title, time_str, f"Checklist: {', '.join(checklist)}" if checklist else ''))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": f"Saved to your {category}!"})

# ---------------------------------------------------------------------------
# API: Chat & Assistant Engine
# ---------------------------------------------------------------------------
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    tone = data.get('tone', 'friendly')
    user_name = data.get('userName', 'Mayur')
    assistant_name = data.get('assistantName', 'Zara')

    if not user_message:
        return jsonify({"status": "error", "message": "Empty message"}), 400

    reply = process_user_query(user_message, tone=tone, user_name=user_name, assistant_name=assistant_name)

    return jsonify({
        "status": "success",
        "reply": reply,
        "tone": tone
    })

# ---------------------------------------------------------------------------
# API: Tasks CRUD & Duplicate Detection
# ---------------------------------------------------------------------------
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "tasks": tasks})

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json or {}
    title = data.get('title', '').strip()
    due_date = data.get('due_date', 'Today')
    priority = data.get('priority', 'Medium')
    estimated_minutes = data.get('estimated_minutes', 30)
    notes = data.get('notes', '')
    source = data.get('source', 'user')

    if not title:
        return jsonify({"status": "error", "message": "Task title is required"}), 400

    force = data.get('force', False)
    if not force:
        duplicates = check_duplicate_task(title)
        if duplicates:
            return jsonify({
                "status": "possible_duplicate",
                "message": f"Possible duplicate task detected: '{duplicates[0]['title']}'. Do you still want to create it?",
                "duplicate": duplicates[0]
            })

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (title, due_date, priority, status, estimated_minutes, notes, source)
        VALUES (?, ?, ?, 'pending', ?, ?, ?)
    ''', (title, due_date, priority, estimated_minutes, notes, source))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "Task created", "task_id": task_id})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    
    if 'status' in data:
        cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (data['status'], task_id))
    if 'due_date' in data:
        cursor.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (data['due_date'], task_id))
    if 'priority' in data:
        cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (data['priority'], task_id))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Task updated"})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Task deleted"})

# ---------------------------------------------------------------------------
# API: Documents & Notes (Upload, List, Delete)
# ---------------------------------------------------------------------------
@app.route('/api/documents', methods=['GET'])
def get_documents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, filename, category, uploaded_at, SUBSTR(content, 1, 150) as snippet FROM documents ORDER BY id DESC")
    docs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"status": "success", "documents": docs})

@app.route('/api/documents', methods=['POST'])
def add_document():
    data = request.json or {}
    title = data.get('title', '').strip()
    filename = data.get('filename', 'note.txt').strip()
    content = data.get('content', '').strip()
    category = data.get('category', 'Note')

    if not title or not content:
        return jsonify({"status": "error", "message": "Title and content are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (title, filename, content, category)
        VALUES (?, ?, ?, ?)
    ''', (title, filename, content, category))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()

    return jsonify({"status": "success", "message": "Document added", "doc_id": doc_id})

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Document deleted"})

# ---------------------------------------------------------------------------
# API: Schedule & Briefing Data
# ---------------------------------------------------------------------------
@app.route('/api/briefing', methods=['GET'])
def get_briefing():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM schedule WHERE date_str = 'Today'")
    schedule_rows = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY id DESC")
    tasks = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT value FROM settings WHERE key = 'user_name'")
    u_row = cursor.fetchone()
    user_name = u_row['value'] if u_row else 'Mayur'
    
    conn.close()
    
    return jsonify({
        "status": "success",
        "data": {
            "userName": user_name,
            "schedule": schedule_rows,
            "tasks": tasks
        }
    })

# ---------------------------------------------------------------------------
# API: Service Integrations & Data Privacy
# ---------------------------------------------------------------------------
@app.route('/api/integrations/status', methods=['GET'])
def get_integrations_status():
    status = IntegrationManager.get_status()
    return jsonify({"status": "success", "integrations": status})

@app.route('/api/integrations/gmail/connect', methods=['POST'])
def connect_gmail():
    data = request.json or {}
    email = data.get('email', 'mayur@gmail.com')
    IntegrationManager.connect_gmail(email)
    return jsonify({"status": "success", "message": f"Connected to Gmail ({email}) via official OAuth 2.0 flow."})

@app.route('/api/integrations/gmail/disconnect', methods=['POST'])
def disconnect_gmail():
    IntegrationManager.disconnect_gmail()
    return jsonify({"status": "success", "message": "Gmail disconnected and stored email tokens removed."})

@app.route('/api/integrations/gmail/emails', methods=['GET'])
def get_gmail_messages():
    status = IntegrationManager.get_status()
    if not status['gmail']['connected']:
        return jsonify({"status": "error", "message": "Gmail is not connected. Connect Gmail first."}), 400
    emails = IntegrationManager.get_gmail_messages()
    return jsonify({"status": "success", "emails": emails})

@app.route('/api/integrations/erp/assignments', methods=['GET'])
def get_erp_assignments():
    assignments = IntegrationManager.get_erp_assignments()
    return jsonify({"status": "success", "assignments": assignments})

@app.route('/api/integrations/erp/submit-preview', methods=['POST'])
def erp_submit_preview():
    data = request.json or {}
    asn_id = data.get('assignment_id')
    file_name = data.get('file_name', 'assignment_solution.pdf')
    
    preview = IntegrationManager.prepare_erp_submission_preview(asn_id, file_name)
    if not preview:
        return jsonify({"status": "error", "message": "Assignment not found"}), 404
        
    return jsonify({"status": "success", "preview": preview})

@app.route('/api/integrations/erp/confirm-submit', methods=['POST'])
def erp_confirm_submit():
    data = request.json or {}
    asn_id = data.get('assignment_id')
    file_name = data.get('file_name')
    
    result = IntegrationManager.confirm_erp_submission(asn_id, file_name)
    return jsonify({"status": "success", "result": result})

@app.route('/api/integrations/whatsapp/forward', methods=['POST'])
def whatsapp_forward():
    data = request.json or {}
    sender = data.get('sender', 'Friend')
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({"status": "error", "message": "Message text is required"}), 400
        
    IntegrationManager.forward_whatsapp_message(sender, text)
    return jsonify({"status": "success", "message": f"Forwarded message saved to AI notes from {sender}."})

@app.route('/api/integrations/whatsapp/forwards', methods=['GET'])
def get_whatsapp_forwards():
    forwards = IntegrationManager.get_whatsapp_forwards()
    return jsonify({"status": "success", "forwards": forwards})

@app.route('/api/integrations/gmail/scan-calendar', methods=['POST'])
def scan_gmail_calendar():
    added = IntegrationManager.scan_gmail_and_sync_calendar()
    return jsonify({"status": "success", "message": f"Scanned Gmail! Added {added} exam date(s) directly to Zara's Calendar.", "added_count": added})

@app.route('/api/integrations/nxtwave/data', methods=['GET'])
def get_nxtwave_data():
    data = IntegrationManager.get_nxtwave_data()
    return jsonify({"status": "success", "nxtwave": data})

@app.route('/api/integrations/nxtwave/connect', methods=['POST'])
def connect_nxtwave():
    data = request.json or {}
    user_id = data.get('user_id', 'MAYUR_NXT_8921')
    IntegrationManager.connect_nxtwave(user_id)
    return jsonify({"status": "success", "message": f"Connected to NxtWave Platform (Student ID: {user_id})!"})

@app.route('/api/data/delete-all', methods=['POST'])
def delete_all_data():
    IntegrationManager.delete_all_user_data()
    init_db()
    return jsonify({"status": "success", "message": "All user data deleted and database reset to fresh default."})

if __name__ == '__main__':
    print("Starting My Personal AI server with Laptop Admin Control & Integrations on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=True)
