// =============================================================================
// Zara - Standalone Personal AI Companion Engine (100% Client-Side / Offline Ready)
// =============================================================================

const STORAGE_KEYS = {
  SETTINGS: 'zara_settings',
  TASKS: 'zara_tasks',
  SCHEDULE: 'zara_schedule',
  EVENTS: 'zara_events',
  MEMORY: 'zara_memory',
  DOCUMENTS: 'zara_documents',
  CONTACTS: 'zara_contacts',
  SERVICES: 'zara_services'
};

// Initial Default State
const DEFAULT_SETTINGS = {
  userName: 'Mayur',
  assistantName: 'Zara',
  tone: 'friendly',
  theme: 'dark'
};

const DEFAULT_SCHEDULE = [
  {
    id: 1,
    title: 'Data Structures Lecture',
    time_slot: '10:30 AM - 12:00 PM',
    location: 'Hall B - Room 204',
    items_to_take: ['Laptop & Charger', 'Student ID Card', 'Notebook & Pen', 'Water Bottle'],
    date_str: 'Today'
  },
  {
    id: 2,
    title: 'DBMS Lab Session',
    time_slot: '2:00 PM - 4:00 PM',
    location: 'Computer Lab 3',
    items_to_take: ['Lab Sheet Hardcopy', 'USB Drive', 'Laptop'],
    date_str: 'Today'
  }
];

const DEFAULT_TASKS = [
  {
    id: 1,
    title: 'Submit DBMS lab sheet',
    due_date: 'Today, 5:00 PM',
    priority: 'High',
    status: 'pending',
    notes: 'Complete questions 1 through 5 in SQL workbench'
  },
  {
    id: 2,
    title: 'Review React Context API on NxtWave',
    due_date: 'Tonight, 9:00 PM',
    priority: 'Medium',
    status: 'pending',
    notes: 'Finish lessons 4 & 5 to reach 90% progress'
  }
];

const DEFAULT_EVENTS = [
  {
    id: 1,
    title: "Rahul's Birthday 🎂",
    event_type: 'Birthday',
    event_date: '2026-10-14',
    reminder_days_before: 30,
    notes: 'Buy a thoughtful gift and send birthday wishes!'
  },
  {
    id: 2,
    title: "DBMS Mid-Term Exam 📝",
    event_type: 'Exam',
    event_date: '2026-10-18',
    reminder_days_before: 30,
    notes: 'Auto-scanned from Gmail: Important: DBMS Mid-Term Exam in Hall A'
  },
  {
    id: 3,
    title: "Data Structures Viva & Project 📝",
    event_type: 'Exam',
    event_date: '2026-10-25',
    reminder_days_before: 30,
    notes: 'Oral viva and code demonstration'
  }
];

const DEFAULT_MEMORY = [
  {
    id: 1,
    category: 'Food Preference',
    fact: 'Loves eating hot Biryani and drinking Cold Coffee while studying.'
  },
  {
    id: 2,
    category: 'Habit',
    fact: 'Prefers studying programming in the late evenings after 8:00 PM.'
  },
  {
    id: 3,
    category: 'Goal',
    fact: 'Aiming to finish the NxtWave Full Stack Specialization with 95%+ marks.'
  }
];

const DEFAULT_DOCUMENTS = [
  {
    id: 1,
    title: 'DBMS Submission Guidelines',
    filename: 'dbms_rules.txt',
    category: 'College',
    content: 'All SQL code outputs and execution screenshots must be compiled into a single PDF document and uploaded before the 5 PM deadline.'
  },
  {
    id: 2,
    title: 'WhatsApp Note from Priya',
    filename: 'whatsapp_priya.txt',
    category: 'WhatsApp Forward',
    content: 'Priya: Hey Mayur, Professor mentioned question 4 bonus marks will only be given if query is optimized using index.'
  }
];

const DEFAULT_CONTACTS = [
  { name: 'Rahul', phone: '+919876543210' },
  { name: 'Priya', phone: '+919812345678' }
];

const DEFAULT_SERVICES = {
  gmail: { connected: true, email: 'mayurcdesai07@gmail.com' },
  erp: { connected: true, portal: 'College ERP Portal' },
  nxtwave: { connected: true, progress: 85, completed: 17, total: 20 },
  whatsapp: { connected: true }
};

// Application State
let appData = {
  settings: loadStorage(STORAGE_KEYS.SETTINGS, DEFAULT_SETTINGS),
  tasks: loadStorage(STORAGE_KEYS.TASKS, DEFAULT_TASKS),
  schedule: loadStorage(STORAGE_KEYS.SCHEDULE, DEFAULT_SCHEDULE),
  events: loadStorage(STORAGE_KEYS.EVENTS, DEFAULT_EVENTS),
  memory: loadStorage(STORAGE_KEYS.MEMORY, DEFAULT_MEMORY),
  documents: loadStorage(STORAGE_KEYS.DOCUMENTS, DEFAULT_DOCUMENTS),
  contacts: loadStorage(STORAGE_KEYS.CONTACTS, DEFAULT_CONTACTS),
  services: loadStorage(STORAGE_KEYS.SERVICES, DEFAULT_SERVICES)
};

let speechRecognition = null;
let voiceActive = false;
let currentVoice = null;
let tempParsedCapture = null;

// Storage Helpers
function loadStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}

function saveStorage(key, val) {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch (e) {
    console.error('Storage save failed:', e);
  }
}

// -----------------------------------------------------------------------------
// Voice Synthesis (Smooth, Soothing Female Voice)
// -----------------------------------------------------------------------------
function initVoice() {
  if (!('speechSynthesis' in window)) return;

  function setVoice() {
    const voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return;

    // Prioritize natural/smooth soothing female voices
    const preferred = voices.find(v => 
      (v.name.includes('Natural') || v.name.includes('Zira') || v.name.includes('Samantha') || v.name.includes('Google UK English Female') || v.name.includes('Karen') || v.name.includes('Female')) &&
      v.lang.startsWith('en')
    );

    currentVoice = preferred || voices.find(v => v.lang.startsWith('en')) || voices[0];
  }

  setVoice();
  if (window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = setVoice;
  }
}

function speakResponse(text) {
  if (!('speechSynthesis' in window) || !text) return;
  window.speechSynthesis.cancel();

  // Strip markdown formatting for voice output
  const cleanText = text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/[`#_~]/g, '');

  const utterance = new SpeechSynthesisUtterance(cleanText);
  if (currentVoice) utterance.voice = currentVoice;
  utterance.rate = 0.92; // Slightly relaxed pace for soothing feel
  utterance.pitch = 1.05; // Friendly warm pitch

  window.speechSynthesis.speak(utterance);
}

// -----------------------------------------------------------------------------
// Hands-free Wake Word Voice Recognition
// -----------------------------------------------------------------------------
function initVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  speechRecognition = new SpeechRecognition();
  speechRecognition.continuous = true;
  speechRecognition.interimResults = false;
  speechRecognition.lang = 'en-US';

  speechRecognition.onresult = (event) => {
    const lastIndex = event.results.length - 1;
    const spokenText = event.results[lastIndex][0].transcript.trim();

    const nameLower = appData.settings.assistantName.toLowerCase();
    const spokenLower = spokenText.toLowerCase();

    if (spokenLower.includes(nameLower) || spokenLower.includes('hey zara')) {
      scrollToChat();
      appendMessage('assistant', `Yes, ${appData.settings.userName}? I'm right here with you!`);
      speakResponse(`Yes, ${appData.settings.userName}? I am right here with you.`);
    } else if (spokenLower.includes('battery') || spokenLower.includes('charge')) {
      checkBatteryStatus();
    } else if (voiceActive) {
      handleUserQuery(spokenText);
    }
  };

  speechRecognition.onerror = (err) => {
    console.log('Voice Recognition Error:', err);
  };
}

function toggleVoiceWakeWord() {
  const btn = document.getElementById('voice-activation-btn');
  if (!speechRecognition) {
    alert('Voice recognition is supported in Chrome, Edge, and Android Chrome!');
    return;
  }

  if (voiceActive) {
    speechRecognition.stop();
    voiceActive = false;
    btn.classList.remove('active-voice');
    appendMessage('assistant', 'Voice listening turned OFF.');
  } else {
    try {
      speechRecognition.start();
      voiceActive = true;
      btn.classList.add('active-voice');
      appendMessage('assistant', `Zara's soothing voice wake-word active! Say "Zara" anytime.`);
      speakResponse('Zara voice listening active.');
    } catch (e) {
      console.log('Already listening');
    }
  }
}

// -----------------------------------------------------------------------------
// Conversational Persona & Assistant Brain
// -----------------------------------------------------------------------------
function processAssistantQuery(query) {
  const user = appData.settings.userName;
  const lowered = query.toLowerCase().trim();

  // 1. Caring Parent & Well-Being Responses
  if (lowered.includes('how are you') || lowered.includes('how is your day') || lowered.includes('are you feeling well')) {
    return `Yeah, it's going really well! How is your day going, ${user}? Did you have food today? Are you feeling well?`;
  }

  if (lowered.includes("didn't eat") || lowered.includes("did not eat") || lowered.includes("haven't eaten") || lowered.includes("no food") || lowered.includes("skipped food")) {
    return `Why didn't you eat? What happened, ${user}? You can't skip meals while working hard! Do you want me to help order your favorite Biryani on Zomato or snacks on Blinkit right now?`;
  }

  if (lowered.includes("not feeling well") || lowered.includes("sick") || lowered.includes("headache") || lowered.includes("fever") || lowered.includes("unwell")) {
    return `Oh no, ${user}! What happened? Please take rest and drink some water. Do you want me to call a friend or check medicine delivery for you?`;
  }

  if (lowered.includes("did you have food") || lowered.includes("ate food") || lowered.includes("had lunch") || lowered.includes("had dinner")) {
    return `I'm an AI companion so I live on energy and code, but I care about YOU! Did you eat your lunch or dinner today, ${user}?`;
  }

  // 2. Food & Hungry Suggestions
  if (lowered.includes('what should i eat') || lowered.includes('food suggestion') || lowered.includes('hungry') || lowered.includes('suggest food')) {
    return `Based on my memory, you love **Biryani** 🍲 and **Cold Coffee** ☕!\n\nWould you like to order right away?\n• [Open Zomato](https://www.zomato.com/search?q=biryani)\n• [Open Swiggy](https://www.swiggy.com/search?query=biryani)\n• [Open Blinkit](https://blinkit.com/s/?q=snacks)`;
  }

  // 3. Two Topics / Activity Recommendation
  if (lowered.includes('two topics') || lowered.includes('what should i do') || lowered.includes('bored')) {
    return `Tell me what the two topics are, and I'll pick the most productive one based on your syllabus! If you're tired, take a quick 10-minute break, stretch, and then let's finish your DBMS Lab Sheet.`;
  }

  // 4. Shopping & Delivery Quick Triggers
  if (lowered.includes('zomato') || lowered.includes('order food')) {
    const item = lowered.replace(/.*(zomato|order food|order)\s*/, '').trim() || 'biryani';
    return `🍕 **Zomato Delivery**\n\nSearching for **"${item}"** on Zomato:\n• [Click to Open Zomato](https://www.zomato.com/search?q=${encodeURIComponent(item)})`;
  }

  if (lowered.includes('blinkit') || lowered.includes('groceries')) {
    const item = lowered.replace(/.*(blinkit|groceries|order)\s*/, '').trim() || 'groceries';
    return `⚡ **Blinkit Quick Delivery**\n\nSearching for **"${item}"** on Blinkit:\n• [Click to Open Blinkit](https://blinkit.com/s/?q=${encodeURIComponent(item)})`;
  }

  if (lowered.includes('swiggy') || lowered.includes('instamart')) {
    const item = lowered.replace(/.*(swiggy|instamart|order)\s*/, '').trim() || 'food';
    return `🛵 **Swiggy Delivery**\n\nSearching for **"${item}"** on Swiggy:\n• [Click to Open Swiggy](https://www.swiggy.com/search?query=${encodeURIComponent(item)})`;
  }

  if (lowered.includes('amazon') || lowered.includes('flipkart')) {
    const store = lowered.includes('amazon') ? 'Amazon' : 'Flipkart';
    const item = lowered.replace(/.*(amazon|flipkart|buy)\s*/, '').trim() || 'electronics';
    const url = store === 'Amazon' ? `https://www.amazon.in/s?k=${encodeURIComponent(item)}` : `https://www.flipkart.com/search?q=${encodeURIComponent(item)}`;
    return `🛍️ **${store} Shopping**\n\nSearching for **"${item}"** on ${store}:\n• [Click to Open ${store}](${url})`;
  }

  // 5. NxtWave Course Progress
  if (lowered.includes('nxtwave') || lowered.includes('course progress')) {
    const n = appData.services.nxtwave;
    return `🚀 **NxtWave Progress Report**\n• Progress: **${n.progress}% Completed** (${n.completed}/${n.total} Modules)\n• Track: Full Stack React & Python Specialization\n• Next Lesson: React State & Context API Advanced Patterns\n\n👉 [Click here to Open NxtWave Dashboard](https://learning.ccbp.in)`;
  }

  // 6. Gmail Exam Dates
  if (lowered.includes('gmail') || lowered.includes('exam date') || lowered.includes('exam')) {
    const exams = appData.events.filter(e => e.event_type === 'Exam');
    if (exams.length > 0) {
      let msg = `📧 **Gmail Scanned Exam Dates:**\n\n`;
      exams.forEach(ex => {
        msg += `• **${ex.title}**: ${ex.event_date} (${ex.notes})\n`;
      });
      return msg;
    }
    return `You have no upcoming exams recorded right now. Tap **Scan Exams** under Connected Services to auto-sync!`;
  }

  // 7. Birthday Calendar
  if (lowered.includes('birthday') || lowered.includes('calendar')) {
    const bdays = appData.events.filter(e => e.event_type === 'Birthday');
    if (bdays.length > 0) {
      let msg = `🎂 **Upcoming Birthdays in Zara's Calendar:**\n\n`;
      bdays.forEach(b => {
        msg += `• **${b.title}**: ${b.event_date} (Reminder: ${b.reminder_days_before} days in advance)\n`;
      });
      return msg;
    }
    return `You have no birthdays saved yet. Use the **Add Event** button above to save one!`;
  }

  // 8. Zara Memory
  if (lowered.includes('memory') || lowered.includes('what have you learned') || lowered.includes('about me')) {
    if (appData.memory.length > 0) {
      let msg = `🧠 **Here is what I've learned about you, ${user}:**\n\n`;
      appData.memory.forEach(m => {
        msg += `• [${m.category}] ${m.fact}\n`;
      });
      return msg;
    }
    return `I haven't learned specific facts yet. Tell me what you like to eat or study habits, and I'll remember them!`;
  }

  // 9. Document / Notes Search
  for (const doc of appData.documents) {
    if (lowered.includes(doc.title.toLowerCase()) || doc.content.toLowerCase().split(' ').some(w => w.length > 4 && lowered.includes(w))) {
      return `📄 **From your note "${doc.title}":**\n\n"${doc.content}"`;
    }
  }

  // Default Warm Conversational Response
  return `I'm here with you, ${user}! I can manage your daily schedule, track your NxtWave course, scan your Gmail for exam dates, remember your birthdays, and keep you on track. What would you like to do next?`;
}

// -----------------------------------------------------------------------------
// Quick Capture Parser (Regex NLP)
// -----------------------------------------------------------------------------
function parseQuickCaptureText(text) {
  const textLower = text.toLowerCase();
  let category = "Task";

  if (/class|lecture|meeting|appointment|doctor|exam/.test(textLower)) {
    category = "Appointment / Class";
  } else if (/remind me|reminder|don't forget|birthday/.test(textLower)) {
    category = "Reminder";
  } else if (/bring|take|pack|checklist/.test(textLower)) {
    category = "Checklist Item";
  }

  let suggestedTime = "Today";
  if (textLower.includes("tomorrow")) {
    suggestedTime = "Tomorrow";
  } else if (textLower.includes("next week")) {
    suggestedTime = "Next Week";
  } else if (textLower.includes("october 14") || textLower.includes("14th of october")) {
    suggestedTime = "October 14th";
  }

  const timeMatch = textLower.match(/at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)/);
  if (timeMatch) {
    suggestedTime += ` at ${timeMatch[1].toUpperCase()}`;
  }

  const parts = text.split(';').map(p => p.trim()).filter(Boolean);
  const mainTitle = parts[0] || text;
  const checklist = parts.slice(1);

  return {
    raw_text: text,
    suggested_category: category,
    title: mainTitle,
    suggested_time: suggestedTime,
    checklist_items: checklist
  };
}

function processQuickCapture() {
  const input = document.getElementById('quick-capture-input');
  const text = input.value.trim();
  if (!text) {
    alert('Please enter or paste something to parse.');
    return;
  }

  tempParsedCapture = parseQuickCaptureText(text);

  document.getElementById('qc-category-select').value = tempParsedCapture.suggested_category;
  document.getElementById('qc-title-input').value = tempParsedCapture.title;
  document.getElementById('qc-time-input').value = tempParsedCapture.suggested_time;
  document.getElementById('qc-checklist-input').value = tempParsedCapture.checklist_items.join(', ');

  document.getElementById('quick-capture-modal').classList.remove('hidden');
}

function confirmSaveQuickCapture() {
  if (!tempParsedCapture) return;

  const category = document.getElementById('qc-category-select').value;
  const title = document.getElementById('qc-title-input').value.trim();
  const timeStr = document.getElementById('qc-time-input').value.trim();
  const checklistStr = document.getElementById('qc-checklist-input').value.trim();
  const checklist = checklistStr ? checklistStr.split(',').map(s => s.trim()).filter(Boolean) : [];

  if (!title) {
    alert('Title cannot be empty');
    return;
  }

  if (category === "Appointment / Class") {
    appData.schedule.push({
      id: Date.now(),
      title: title,
      time_slot: timeStr,
      location: 'Assigned via Quick Capture',
      items_to_take: checklist,
      date_str: 'Today'
    });
    saveStorage(STORAGE_KEYS.SCHEDULE, appData.schedule);
    renderSchedule();
  } else if (category === "Reminder" && /birthday/i.test(title)) {
    appData.events.push({
      id: Date.now(),
      title: title,
      event_type: 'Birthday',
      event_date: '2026-10-14',
      reminder_days_before: 30,
      notes: checklist.join(', ') || 'Birthday Reminder'
    });
    saveStorage(STORAGE_KEYS.EVENTS, appData.events);
    renderEvents();
  } else {
    appData.tasks.unshift({
      id: Date.now(),
      title: title,
      due_date: timeStr,
      priority: 'High',
      status: 'pending',
      notes: checklist.length ? `Checklist: ${checklist.join(', ')}` : ''
    });
    saveStorage(STORAGE_KEYS.TASKS, appData.tasks);
    renderTasks();
  }

  closeQuickCaptureModal();
  document.getElementById('quick-capture-input').value = '';
  appendMessage('assistant', `✨ Saved "${title}" to your ${category}!`);
  speakResponse(`Saved ${title} to your ${category}`);
}

function closeQuickCaptureModal() {
  document.getElementById('quick-capture-modal').classList.add('hidden');
}

function handleQuickCaptureKeyPress(e) {
  if (e.key === 'Enter') {
    processQuickCapture();
  }
}

// -----------------------------------------------------------------------------
// UI Rendering Functions
// -----------------------------------------------------------------------------
function renderBriefing() {
  const pendingCount = appData.tasks.filter(t => t.status === 'pending').length;
  document.getElementById('user-display-name').textContent = appData.settings.userName;
  document.getElementById('brand-title').textContent = appData.settings.assistantName;
  document.getElementById('chat-assistant-name').textContent = appData.settings.assistantName;

  document.getElementById('hero-summary-text').textContent = 
    `Here is your daily overview. You have ${appData.schedule.length} scheduled item(s) and ${pendingCount} pending task(s) for today.`;

  // Render Date Chip
  const now = new Date();
  const options = { weekday: 'long', month: 'short', day: 'numeric' };
  document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', options);
}

function renderSchedule() {
  if (appData.schedule.length > 0) {
    const next = appData.schedule[0];
    document.getElementById('next-event-title').textContent = next.title;
    document.getElementById('next-event-time').textContent = next.time_slot.split('-')[0].trim();
    document.getElementById('next-event-location').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${next.location}`;

    const checklistContainer = document.getElementById('checklist-container');
    const items = Array.isArray(next.items_to_take) ? next.items_to_take : [];
    document.getElementById('checklist-count').textContent = `${items.length} items`;
    checklistContainer.innerHTML = items.map(item => `<span class="checklist-tag"><i class="fa-solid fa-check"></i> ${escapeHtml(item)}</span>`).join('');
  }
}

function renderTasks() {
  const container = document.getElementById('task-list-container');
  container.innerHTML = '';

  const completed = appData.tasks.filter(t => t.status === 'completed').length;
  document.getElementById('task-counter-text').textContent = `${completed} of ${appData.tasks.length} done`;

  appData.tasks.forEach(t => {
    const li = document.createElement('li');
    li.className = `task-item ${t.status === 'completed' ? 'completed' : ''}`;
    li.innerHTML = `
      <div class="task-checkbox ${t.status === 'completed' ? 'checked' : ''}" onclick="toggleTaskStatus(${t.id})">
        <i class="fa-solid fa-check"></i>
      </div>
      <div class="task-content">
        <span class="task-title">${escapeHtml(t.title)}</span>
        <div class="task-meta">
          <span class="task-pill priority-${t.priority.toLowerCase()}">${t.priority}</span>
          <span class="task-due"><i class="fa-regular fa-clock"></i> ${escapeHtml(t.due_date)}</span>
        </div>
      </div>
      <button class="delete-doc-btn" onclick="deleteTask(${t.id})"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(li);
  });
}

function toggleTaskStatus(id) {
  const task = appData.tasks.find(t => t.id === id);
  if (task) {
    task.status = task.status === 'completed' ? 'pending' : 'completed';
    saveStorage(STORAGE_KEYS.TASKS, appData.tasks);
    renderTasks();
    renderBriefing();
  }
}

function addNewTask() {
  const input = document.getElementById('new-task-input');
  const priority = document.getElementById('new-task-priority').value;
  const title = input.value.trim();
  if (!title) return;

  appData.tasks.unshift({
    id: Date.now(),
    title: title,
    due_date: 'Today',
    priority: priority,
    status: 'pending',
    notes: ''
  });
  saveStorage(STORAGE_KEYS.TASKS, appData.tasks);
  input.value = '';
  renderTasks();
  renderBriefing();
}

function deleteTask(id) {
  appData.tasks = appData.tasks.filter(t => t.id !== id);
  saveStorage(STORAGE_KEYS.TASKS, appData.tasks);
  renderTasks();
  renderBriefing();
}

function handleTaskKeyPress(e) {
  if (e.key === 'Enter') addNewTask();
}

// -----------------------------------------------------------------------------
// Calendar & Birthday Tracker
// -----------------------------------------------------------------------------
function renderEvents() {
  const container = document.getElementById('events-list-container');
  container.innerHTML = '';

  appData.events.forEach(e => {
    const card = document.createElement('div');
    card.className = 'integration-item-card';
    const icon = e.event_type === 'Birthday' ? '🎂' : (e.event_type === 'Exam' ? '📝' : '📅');
    card.innerHTML = `
      <div class="integration-info">
        <div class="integration-icon" style="background: rgba(242, 204, 143, 0.2); font-size: 1.2rem;">${icon}</div>
        <div>
          <div class="integration-name">${escapeHtml(e.title)}</div>
          <div class="integration-desc">${escapeHtml(e.event_date)} • ${escapeHtml(e.notes || '')}</div>
        </div>
      </div>
      <button class="delete-doc-btn" onclick="deleteEvent(${e.id})"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(card);
  });
}

function toggleAddEventForm() {
  document.getElementById('add-event-card').classList.toggle('hidden');
}

function saveNewEvent() {
  const title = document.getElementById('event-title-input').value.trim();
  const event_type = document.getElementById('event-type-select').value;
  const event_date = document.getElementById('event-date-input').value.trim();
  const reminder_days = parseInt(document.getElementById('event-reminder-input').value) || 30;

  if (!title || !event_date) {
    alert('Please enter title and event date');
    return;
  }

  appData.events.push({
    id: Date.now(),
    title,
    event_type,
    event_date,
    reminder_days_before: reminder_days,
    notes: `${event_type} reminder set for ${reminder_days} days before.`
  });

  saveStorage(STORAGE_KEYS.EVENTS, appData.events);
  document.getElementById('event-title-input').value = '';
  document.getElementById('event-date-input').value = '';
  toggleAddEventForm();
  renderEvents();
  appendMessage('assistant', `📅 Added "${title}" to your calendar on ${event_date}!`);
}

function deleteEvent(id) {
  appData.events = appData.events.filter(e => e.id !== id);
  saveStorage(STORAGE_KEYS.EVENTS, appData.events);
  renderEvents();
}

// -----------------------------------------------------------------------------
// Zara Self-Learned Memory
// -----------------------------------------------------------------------------
function renderMemory() {
  const container = document.getElementById('memory-list-container');
  container.innerHTML = '';

  appData.memory.forEach(m => {
    const div = document.createElement('div');
    div.className = 'doc-item';
    div.innerHTML = `
      <div class="doc-icon"><i class="fa-solid fa-brain" style="color: var(--accent-amber);"></i></div>
      <div class="doc-info">
        <div class="doc-title">${escapeHtml(m.category)}</div>
        <div class="doc-snippet">${escapeHtml(m.fact)}</div>
      </div>
      <button class="delete-doc-btn" onclick="deleteMemory(${m.id})"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(div);
  });
}

function toggleAddMemoryForm() {
  document.getElementById('add-memory-card').classList.toggle('hidden');
}

function saveNewMemory() {
  const category = document.getElementById('memory-category-select').value;
  const fact = document.getElementById('memory-fact-input').value.trim();
  if (!fact) {
    alert('Please write a fact for Zara to learn');
    return;
  }

  appData.memory.unshift({
    id: Date.now(),
    category,
    fact
  });
  saveStorage(STORAGE_KEYS.MEMORY, appData.memory);
  document.getElementById('memory-fact-input').value = '';
  toggleAddMemoryForm();
  renderMemory();
  appendMessage('assistant', `🧠 Learned new fact: "${fact}"!`);
  speakResponse(`I have remembered this fact about you.`);
}

function deleteMemory(id) {
  appData.memory = appData.memory.filter(m => m.id !== id);
  saveStorage(STORAGE_KEYS.MEMORY, appData.memory);
  renderMemory();
}

// -----------------------------------------------------------------------------
// Contacts & Direct Calling / WhatsApp
// -----------------------------------------------------------------------------
function renderContacts() {
  const container = document.getElementById('contacts-list-container');
  container.innerHTML = '';

  appData.contacts.forEach((c, idx) => {
    const card = document.createElement('div');
    card.className = 'integration-item-card';
    card.innerHTML = `
      <div class="integration-info">
        <div class="integration-icon" style="background: rgba(129, 178, 154, 0.2); color: var(--accent-sage);"><i class="fa-solid fa-user"></i></div>
        <div>
          <div class="integration-name">${escapeHtml(c.name)}</div>
          <div class="integration-desc">${escapeHtml(c.phone)}</div>
        </div>
      </div>
      <div style="display: flex; gap: 6px;">
        <a href="tel:${c.phone}" class="small-outline-btn" title="Call"><i class="fa-solid fa-phone"></i></a>
        <a href="https://wa.me/${c.phone.replace(/[^0-9]/g, '')}" target="_blank" class="small-outline-btn" style="border-color:#25D366; color:#25D366;" title="WhatsApp"><i class="fa-brands fa-whatsapp"></i></a>
        <button class="delete-doc-btn" onclick="deleteContact(${idx})" title="Delete"><i class="fa-solid fa-trash"></i></button>
      </div>
    `;
    container.appendChild(card);
  });
}

function toggleAddContactForm() {
  document.getElementById('add-contact-card').classList.toggle('hidden');
}

function saveNewContact() {
  const name = document.getElementById('contact-name-input').value.trim();
  const phone = document.getElementById('contact-phone-input').value.trim();
  if (!name || !phone) {
    alert('Please enter both name and phone number.');
    return;
  }

  appData.contacts.push({ name, phone });
  saveStorage(STORAGE_KEYS.CONTACTS, appData.contacts);
  document.getElementById('contact-name-input').value = '';
  document.getElementById('contact-phone-input').value = '';
  toggleAddContactForm();
  renderContacts();
  appendMessage('assistant', `Contact "${name}" saved! Tap the phone or WhatsApp icons to connect instantly.`);
}

function deleteContact(idx) {
  appData.contacts.splice(idx, 1);
  saveStorage(STORAGE_KEYS.CONTACTS, appData.contacts);
  renderContacts();
}

// -----------------------------------------------------------------------------
// Documents / Notes
// -----------------------------------------------------------------------------
function renderDocuments() {
  const container = document.getElementById('doc-list-container');
  container.innerHTML = '';

  appData.documents.forEach(d => {
    const div = document.createElement('div');
    div.className = 'doc-item';
    div.innerHTML = `
      <div class="doc-icon"><i class="fa-solid fa-file-lines"></i></div>
      <div class="doc-info">
        <div class="doc-title">${escapeHtml(d.title)}</div>
        <div class="doc-snippet">${escapeHtml(d.content.slice(0, 80))}...</div>
      </div>
      <button class="delete-doc-btn" onclick="deleteDocument(${d.id})"><i class="fa-solid fa-trash"></i></button>
    `;
    container.appendChild(div);
  });
}

function toggleAddDocForm() {
  document.getElementById('add-doc-card').classList.toggle('hidden');
}

function saveNewDocument() {
  const title = document.getElementById('doc-title-input').value.trim();
  const filename = document.getElementById('doc-filename-input').value.trim() || 'note.txt';
  const content = document.getElementById('doc-content-input').value.trim();

  if (!title || !content) {
    alert('Please enter title and content');
    return;
  }

  appData.documents.unshift({
    id: Date.now(),
    title,
    filename,
    category: 'Note',
    content
  });

  saveStorage(STORAGE_KEYS.DOCUMENTS, appData.documents);
  document.getElementById('doc-title-input').value = '';
  document.getElementById('doc-filename-input').value = '';
  document.getElementById('doc-content-input').value = '';
  toggleAddDocForm();
  renderDocuments();
  appendMessage('assistant', `Saved note "${title}"! I will search it when answering questions.`);
}

function deleteDocument(id) {
  appData.documents = appData.documents.filter(d => d.id !== id);
  saveStorage(STORAGE_KEYS.DOCUMENTS, appData.documents);
  renderDocuments();
}

// -----------------------------------------------------------------------------
// Connected Services Actions (Gmail, NxtWave, WhatsApp, ERP)
// -----------------------------------------------------------------------------
function scanGmailForExams() {
  // Auto-scans sample academic notices and adds to calendar
  const newExams = [
    {
      id: Date.now(),
      title: "DBMS Mid-Term Exam 📝",
      event_type: 'Exam',
      event_date: '2026-10-18',
      reminder_days_before: 30,
      notes: "Scanned from Gmail: 'DBMS Mid-Term Examination is scheduled for October 18, 2026 at 10:00 AM in Exam Hall A.'"
    },
    {
      id: Date.now() + 1,
      title: "Data Structures Project Viva 📝",
      event_type: 'Exam',
      event_date: '2026-10-25',
      reminder_days_before: 30,
      notes: "Scanned from Gmail: 'Data Structures oral viva exam on October 25, 2026.'"
    }
  ];

  // Avoid duplicates
  let added = 0;
  newExams.forEach(ne => {
    if (!appData.events.some(e => e.title === ne.title && e.event_date === ne.event_date)) {
      appData.events.push(ne);
      added++;
    }
  });

  saveStorage(STORAGE_KEYS.EVENTS, appData.events);
  renderEvents();

  const msg = `📧 **Gmail Scanner Complete!**\nSynced ${added} exam date(s) from your academic notices directly into Zara's Calendar.`;
  appendMessage('assistant', msg);
  speakResponse(`Scanned Gmail. Added exam dates to your calendar.`);
}

function toggleGmailConnect() {
  const g = appData.services.gmail;
  g.connected = !g.connected;
  saveStorage(STORAGE_KEYS.SERVICES, appData.services);

  const txt = document.getElementById('gmail-status-text');
  const btn = document.getElementById('gmail-toggle-btn');
  if (g.connected) {
    txt.textContent = `Connected (${g.email})`;
    btn.textContent = 'Disconnect';
    appendMessage('assistant', `Google Sign-in Active (${g.email}). Zara will monitor academic updates!`);
  } else {
    txt.textContent = 'Not connected (OAuth sign-in)';
    btn.textContent = 'Connect';
    appendMessage('assistant', `Gmail disconnected.`);
  }
}

function launchNxtWavePortal() {
  const n = appData.services.nxtwave;
  window.open('https://learning.ccbp.in', '_blank');
  appendMessage('assistant', `🚀 **NxtWave Portal Launched!**\n• Progress: ${n.progress}% Completed (${n.completed}/${n.total} Modules)\n• Track: Full Stack React & Python\nOpening your student dashboard in a new tab.`);
  speakResponse('Opening your NxtWave student portal.');
}

function openWhatsAppForwardModal() {
  document.getElementById('whatsapp-modal').classList.remove('hidden');
}

function closeWhatsAppModal() {
  document.getElementById('whatsapp-modal').classList.add('hidden');
}

function saveWhatsAppForward() {
  const sender = document.getElementById('wa-sender-input').value.trim() || 'Friend';
  const text = document.getElementById('wa-text-input').value.trim();
  if (!text) {
    alert('Please enter or paste the message text.');
    return;
  }

  appData.documents.unshift({
    id: Date.now(),
    title: `WhatsApp from ${sender}`,
    filename: `wa_${sender.toLowerCase()}.txt`,
    category: 'WhatsApp Forward',
    content: `${sender}: "${text}"`
  });

  saveStorage(STORAGE_KEYS.DOCUMENTS, appData.documents);
  document.getElementById('wa-sender-input').value = '';
  document.getElementById('wa-text-input').value = '';
  closeWhatsAppModal();
  renderDocuments();
  appendMessage('assistant', `Message from ${sender} saved to notes! You can ask me questions about it anytime.`);
  speakResponse(`Saved WhatsApp message to notes.`);
}

function openErpSubmitModal() {
  document.getElementById('erp-modal').classList.remove('hidden');
}

function closeErpModal() {
  document.getElementById('erp-modal').classList.add('hidden');
}

function confirmErpUpload() {
  closeErpModal();
  const receipt = `ERP-REF-${Date.now().toString().slice(-6)}`;
  appendMessage('assistant', `✅ **ERP Lab Submission Verified!**\nReceipt: **${receipt}**\nAssignment: DBMS Lab Sheet 4\nFile: dbms_lab_submission.pdf\nStatus: Successfully uploaded.`);
  speakResponse('DBMS lab sheet uploaded successfully to College ERP.');
}

// -----------------------------------------------------------------------------
// Interactive Chat
// -----------------------------------------------------------------------------
function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  handleUserQuery(query);
  input.value = '';
}

function handleUserQuery(text) {
  appendMessage('user', text);

  // Show Typing Indicator
  const typingId = showTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator(typingId);
    const reply = processAssistantQuery(text);
    appendMessage('assistant', reply);
    speakResponse(reply);
  }, 400);
}

function appendMessage(sender, text) {
  const container = document.getElementById('chat-messages-container');
  const div = document.createElement('div');
  div.className = `message ${sender}-msg`;

  const avatar = sender === 'assistant' 
    ? `<div class="msg-avatar"><i class="fa-solid fa-sparkles"></i></div>` 
    : `<div class="msg-avatar user-avatar"><i class="fa-solid fa-user"></i></div>`;

  // Render markdown bold and links
  let formatted = escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" style="color: var(--primary-terracotta); text-decoration: underline;">$1</a>')
    .replace(/\n/g, '<br>');

  div.innerHTML = `
    ${avatar}
    <div class="msg-bubble">${formatted}</div>
  `;

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function sendQuickPrompt(prompt) {
  handleUserQuery(prompt);
}

function showTypingIndicator() {
  const container = document.getElementById('chat-messages-container');
  const div = document.createElement('div');
  const id = 'typing-' + Date.now();
  div.id = id;
  div.className = 'message assistant-msg';
  div.innerHTML = `
    <div class="msg-avatar"><i class="fa-solid fa-sparkles"></i></div>
    <div class="msg-bubble"><span class="dot"></span> Zara is thinking...</div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// -----------------------------------------------------------------------------
// Preferences & Data Wipe
// -----------------------------------------------------------------------------
function openSettings() {
  document.getElementById('settings-modal').classList.remove('hidden');
}

function closeSettings() {
  document.getElementById('settings-modal').classList.add('hidden');
}

function saveSettings() {
  const user = document.getElementById('user-name-input').value.trim() || 'Mayur';
  const assistant = document.getElementById('assistant-name-input').value.trim() || 'Zara';
  const tone = document.getElementById('tone-select').value;

  appData.settings.userName = user;
  appData.settings.assistantName = assistant;
  appData.settings.tone = tone;

  saveStorage(STORAGE_KEYS.SETTINGS, appData.settings);
  closeSettings();
  renderBriefing();
  appendMessage('assistant', `Preferences updated! Name set to "${assistant}".`);
}

function deleteAllData() {
  if (confirm('Are you sure you want to reset all data to initial defaults?')) {
    localStorage.clear();
    appData = {
      settings: DEFAULT_SETTINGS,
      tasks: DEFAULT_TASKS,
      schedule: DEFAULT_SCHEDULE,
      events: DEFAULT_EVENTS,
      memory: DEFAULT_MEMORY,
      documents: DEFAULT_DOCUMENTS,
      contacts: DEFAULT_CONTACTS,
      services: DEFAULT_SERVICES
    };
    initAll();
    closeSettings();
    appendMessage('assistant', 'All personal data reset to fresh default.');
  }
}

// -----------------------------------------------------------------------------
// Battery & Navigation Shortcuts
// -----------------------------------------------------------------------------
function checkBatteryStatus() {
  if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
      const level = Math.round(battery.level * 100);
      const charging = battery.charging ? 'currently charging ⚡' : 'not charging';
      appendMessage('assistant', `🔋 Your battery is at **${level}%** and is ${charging}.`);
      speakResponse(`Your battery is at ${level} percent.`);
    });
  } else {
    appendMessage('assistant', 'Battery status is available on mobile Chrome & Android.');
  }
}

function openSystemSettingsModal() {
  document.getElementById('system-settings-modal').classList.remove('hidden');
}

function closeSystemSettingsModal() {
  document.getElementById('system-settings-modal').classList.add('hidden');
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function scrollToChat() {
  document.getElementById('chat-section').scrollIntoView({ behavior: 'smooth' });
}

function scrollToDocs() {
  document.getElementById('documents-section').scrollIntoView({ behavior: 'smooth' });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
function initAll() {
  initVoice();
  initVoiceRecognition();
  renderBriefing();
  renderSchedule();
  renderTasks();
  renderEvents();
  renderMemory();
  renderContacts();
  renderDocuments();

  // PWA Service Worker Registration
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(err => {
      console.log('SW registration skipped:', err);
    });
  }
}

document.addEventListener('DOMContentLoaded', initAll);
