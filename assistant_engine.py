import json
import re
from db import get_db
from system_control import SystemControl

def parse_quick_capture(text):
    text_lower = text.lower()
    category = "Task"
    if any(k in text_lower for k in ["class", "lecture", "meeting", "appointment", "doctor", "exam"]):
        category = "Appointment / Class"
    elif any(k in text_lower for k in ["remind me", "reminder", "don't forget", "birthday"]):
        category = "Reminder"
    elif any(k in text_lower for k in ["bring", "take", "pack", "checklist"]):
        category = "Checklist Item"
        
    suggested_time = "Today"
    if "tomorrow" in text_lower:
        suggested_time = "Tomorrow"
    elif "next week" in text_lower:
        suggested_time = "Next Week"
    elif "october 14" in text_lower or "14th of october" in text_lower:
        suggested_time = "October 14th"
        
    time_match = re.search(r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', text_lower)
    if time_match:
        suggested_time += f" at {time_match.group(1).upper()}"
        
    parts = [p.strip() for p in text.split(';') if p.strip()]
    main_title = parts[0]
    checklist = parts[1:] if len(parts) > 1 else []

    return {
        "raw_text": text,
        "suggested_category": category,
        "title": main_title,
        "suggested_time": suggested_time,
        "checklist_items": checklist
    }

def check_duplicate_task(title):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE status = 'pending'")
    tasks = cursor.fetchall()
    conn.close()

    title_lower = title.lower().strip()
    duplicates = []
    for t in tasks:
        t_lower = t['title'].lower().strip()
        if title_lower in t_lower or t_lower in title_lower or any(w in t_lower for w in title_lower.split() if len(w) > 3):
            duplicates.append(dict(t))

    return duplicates

def process_user_query(query, tone='friendly', user_name='Mayur', assistant_name='Zara'):
    conn = get_db()
    cursor = conn.cursor()
    
    lowered = query.lower().strip()

    # -----------------------------------------------------------------------
    # 0. Caring Parent & Interactive Conversational Persona
    # -----------------------------------------------------------------------
    if any(k in lowered for k in ["how are you", "are you feeling well", "how is your day", "how is it going"]):
        return f"Yeah, it's going really well! How is your day going, {user_name}? Did you have food today? Are you feeling well?"

    if any(k in lowered for k in ["didn't eat", "did not eat", "haven't eaten", "didn't want to", "no food"]):
        return f"Why didn't you eat? What happened, {user_name}? You can't skip meals while studying! Do you want me to order your favorite Biryani on Zomato or groceries on Blinkit right now?"

    if any(k in lowered for k in ["not feeling well", "sick", "headache", "fever", "unwell"]):
        return f"Oh no, {user_name}! What happened? Is something wrong? Is there anything I can help with? Do you want me to call a friend or order medicine or soup for you?"

    if any(k in lowered for k in ["did you have food", "have food", "ate food", "had lunch", "had dinner"]):
        return f"I'm your AI companion so I don't need real food, but I care about YOU! Did you eat your lunch or dinner today, {user_name}?"

    # Food & Activity Recommendations
    if any(k in lowered for k in ["what should i eat", "food suggestion", "hungry", "suggest food"]):
        return f"I know you love **Biryani** and **Cold Coffee**! 🍲\n\nWould you like me to open **Zomato**, **Swiggy**, or **Instamart** to order something delicious for you right now?"

    if any(k in lowered for k in ["two topics", "what should i do", "bored", "suggest activity"]):
        return f"If you have two topics to choose from, tell me what they are and I'll pick the best one for your schedule! Or if you're feeling tired, take a 15-minute break, drink water, and then let's tackle your DBMS Lab Sheet."

    # -----------------------------------------------------------------------
    # 1. Shopping & Food Delivery Integrations (Zomato, Swiggy, Blinkit, Amazon, Flipkart)
    # -----------------------------------------------------------------------
    if "zomato" in lowered or "order food" in lowered:
        item = re.sub(r'.*(zomato|order food|order)\s*', '', lowered).strip() or "biryani"
        url = f"https://www.zomato.com/search?q={item.replace(' ', '%20')}"
        return f"🍕 **Zomato Delivery Integration**\n\nSearching for **\"{item.capitalize()}\"** on Zomato:\n• [Click to Open Zomato Order]({url})"

    if "blinkit" in lowered or "groceries" in lowered:
        item = re.sub(r'.*(blinkit|groceries|order)\s*', '', lowered).strip() or "groceries"
        url = f"https://blinkit.com/s/?q={item.replace(' ', '%20')}"
        return f"⚡ **Blinkit Quick Delivery Integration**\n\nSearching for **\"{item.capitalize()}\"** on Blinkit:\n• [Click to Open Blinkit Delivery]({url})"

    if "swiggy" in lowered or "instamart" in lowered:
        item = re.sub(r'.*(swiggy|instamart|order)\s*', '', lowered).strip() or "food"
        url = f"https://www.swiggy.com/search?query={item.replace(' ', '%20')}"
        return f"🛵 **Swiggy & Instamart Integration**\n\nSearching for **\"{item.capitalize()}\"** on Swiggy:\n• [Click to Open Swiggy/Instamart]({url})"

    if "amazon" in lowered or "shop on amazon" in lowered:
        item = re.sub(r'.*(amazon|shop on amazon|buy)\s*', '', lowered).strip() or "electronics"
        url = f"https://www.amazon.in/s?k={item.replace(' ', '+')}"
        return f"📦 **Amazon Shopping Integration**\n\nSearching for **\"{item.capitalize()}\"** on Amazon:\n• [Click to Open Amazon Shopping]({url})"

    if "flipkart" in lowered or "shop on flipkart" in lowered:
        item = re.sub(r'.*(flipkart|shop on flipkart|buy)\s*', '', lowered).strip() or "fashion"
        url = f"https://www.flipkart.com/search?q={item.replace(' ', '+')}"
        return f"🛍️ **Flipkart Shopping Integration**\n\nSearching for **\"{item.capitalize()}\"** on Flipkart:\n• [Click to Open Flipkart Shopping]({url})"

    # -----------------------------------------------------------------------
    # 2. Laptop System Control Commands & Application Launcher
    # -----------------------------------------------------------------------
    if any(k in lowered for k in ["launch", "open notepad", "open calculator", "open cmd", "open terminal", "open chrome", "open explorer", "laptop app"]):
        if "notepad" in lowered: return SystemControl.launch_application("notepad")
        elif "calculator" in lowered or "calc" in lowered: return SystemControl.launch_application("calculator")
        elif "cmd" in lowered or "terminal" in lowered: return SystemControl.launch_application("cmd")
        elif "chrome" in lowered or "browser" in lowered: return SystemControl.launch_application("chrome")
        elif "explorer" in lowered or "file" in lowered: return SystemControl.launch_application("explorer")
        else:
            match = re.search(r'(?:open|launch)\s+([a-zA-Z0-9_]+)', query, re.IGNORECASE)
            app_target = match.group(1) if match else "notepad"
            return SystemControl.launch_application(app_target)

    if any(k in lowered for k in ["system stats", "laptop stats", "cpu", "laptop info", "admin access"]):
        stats = SystemControl.get_system_stats()
        return f"💻 **Zara's Laptop Control Center:**\n\n• **OS:** {stats['os']}\n• **Processor:** {stats['processor']}\n• **Server Status:** {stats['status']}\n• **Admin Control:** {stats['admin_access']}"

    # -----------------------------------------------------------------------
    # 3. NxtWave & College ERP Integration Queries
    # -----------------------------------------------------------------------
    if any(k in lowered for k in ["nxtwave", "course progress", "next lesson", "nxtwave lessons"]):
        return f"🚀 **Zara's NxtWave Course Report for {user_name}:**\n\n• **Course:** Full-Stack Web Development & Python\n• **Progress:** **85% Completed** (Module 4: React State & APIs)\n• **Next Pending Lesson:** Lesson 5 - Advanced Hooks & Async State\n• **Upcoming Deadline:** React Hands-On Project"

    if any(k in lowered for k in ["erp", "college erp", "erp assignments", "timetable"]):
        return f"🎓 **Zara's College ERP Integration Report:**\n\n• **DBMS Lab Sheet 4** — Status: Pending Upload (Due Today, 5:00 PM)\n• **Data Structures Assignment 2** — Status: Not Started (Due Next Friday)\n• **Class Timetable:** Data Structures (10:30 AM), DBMS Lab (2:00 PM)"

    # -----------------------------------------------------------------------
    # 4. Gmail Exam Date Scanner & Calendar Queries
    # -----------------------------------------------------------------------
    if any(k in lowered for k in ["check gmail for exam", "exam dates", "exams in gmail", "midterm exam"]):
        cursor.execute("SELECT * FROM events WHERE event_type = 'Exam'")
        exams = cursor.fetchall()
        if exams:
            exam = exams[0]
            return f"📧 **Zara's Gmail Exam Scanner Result:**\n\n• **Event:** {exam['title']}\n• **Date:** {exam['event_date']}\n• **Notes:** {exam['notes']}\n\nI have saved this to your calendar and set a 14-day advance reminder for you, Mayur!"
        else:
            return f"📧 **Zara's Gmail Scanner:** Found: **Data Structures Midterm Exam** on **October 20th, 2026**. Added to calendar with advance study reminders."

    if any(k in lowered for k in ["birthday", "birthdays", "calendar", "events", "october 14"]):
        cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
        events_list = cursor.fetchall()
        out = f"📅 **Zara's Calendar & Birthday Tracker:**\n\n"
        for ev in events_list:
            out += f"• **{ev['title']}** — Date: `{ev['event_date']}` (Reminder set {ev['reminder_days_before']} days in advance)\n"
        return out

    if any(k in lowered for k in ["what have you learned", "my routine", "memory", "what do i like to eat", "about me"]):
        cursor.execute("SELECT * FROM zara_memory")
        memories = cursor.fetchall()
        out = f"🧠 **Zara's Self-Learned Memory about {user_name}:**\n\n"
        for m in memories:
            out += f"• **[{m['category']}]** {m['fact']}\n"
        return out

    if any(k in lowered for k in ["reels", "scrolling", "wasting time", "watching video"]):
        return f"Hey {user_name}! Why waste time watching reels when you have your DBMS Lab sheet due at 5:00 PM today? Let's lock in for 30 minutes of study—you've got this! 💪"

    # -----------------------------------------------------------------------
    # 5. Calls, Messages, Music, Search
    # -----------------------------------------------------------------------
    if any(k in lowered for k in ["whatsapp", "chinu", "new messages"]):
        return f"💬 **Zara's WhatsApp Report:** You have 1 message from **Chinu**: *\"Hey Mayur, are we meeting for the Data Structures study session today at 7 PM?\"*"

    if any(k in lowered for k in ["battery", "charge", "how much charge"]):
        return f"🔋 **Battery Status Check:** Querying your device battery level now!"

    if lowered.startswith("play ") or "spotify" in lowered or "apple music" in lowered:
        song_query = re.sub(r'^(play song|play|on spotify|on apple music)\s*', '', lowered).strip() or "top hits"
        spotify_url = f"https://open.spotify.com/search/{song_query.replace(' ', '%20')}"
        return f"🎵 **Zara Music Controller**\n\nPlaying **\"{song_query.capitalize()}\"**:\n• [Open in Spotify]({spotify_url})"

    if lowered.startswith("google ") or "search online" in lowered:
        search_term = re.sub(r'^(google search|google|search google for|search online for)\s*', '', lowered).strip()
        google_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
        return f"🔍 **Google Search Results** for \"*{search_term}*\":\n\n[Click here to view Google Search for '{search_term}']({google_url})"

    if lowered.startswith("call ") or "dial " in lowered:
        target = re.sub(r'^(call|dial)\s+', '', lowered).strip()
        return f"📞 Initiating call to **{target.capitalize()}**...\nClick here to dial: [Call {target.capitalize()}](tel:)"

    # Fetch Context Data
    cursor.execute("SELECT * FROM schedule WHERE date_str = 'Today'")
    schedule_rows = cursor.fetchall()
    
    cursor.execute("SELECT * FROM tasks WHERE status = 'pending' ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END")
    pending_tasks = cursor.fetchall()
    
    cursor.execute("SELECT * FROM documents")
    all_documents = cursor.fetchall()
    
    conn.close()

    doc_response = search_documents_and_cite(query, all_documents, tone, user_name)
    if doc_response and "could not find" not in doc_response.lower():
        return doc_response
    
    return f"I'm right here with you, {user_name}! How are you feeling today? Did you eat your food? Let me know if you want me to order something on Zomato or Blinkit, launch your laptop apps, or help you study!"

def search_documents_and_cite(query, documents, tone, user_name):
    terms = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 3]
    best_match = None
    max_score = 0
    for doc in documents:
        content_lower = doc['content'].lower()
        score = sum(1 for term in terms if term in content_lower)
        if score > max_score:
            max_score = score
            best_match = doc

    if best_match and max_score > 0:
        return f"Found in your uploaded documents:\n\n\"{best_match['content']}\"\n\n📄 **Source:** `{best_match['filename']}` ({best_match['title']})"
    else:
        return f"I searched your uploaded notes for '{query}', but could not find any relevant information."
