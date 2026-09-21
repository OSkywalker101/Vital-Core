import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'vitalcore.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        dosage TEXT NOT NULL, time TEXT NOT NULL,
        taken INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS water_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount INTEGER DEFAULT 200, log_date DATE DEFAULT (date('now')))''')

    c.execute('''CREATE TABLE IF NOT EXISTS diary_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT, mood TEXT NOT NULL,
        sleep_hours REAL DEFAULT 0, water INTEGER DEFAULT 0,
        notes TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE, icon TEXT NOT NULL, target INTEGER DEFAULT 1)''')

    c.execute('''CREATE TABLE IF NOT EXISTS habit_completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL,
        completed_date DATE DEFAULT (date('now')), completion_count INTEGER DEFAULT 1,
        FOREIGN KEY (habit_id) REFERENCES habits(id),
        UNIQUE(habit_id, completed_date))''')

    c.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        phone TEXT NOT NULL, email TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL,
        doctor TEXT NOT NULL, specialty TEXT NOT NULL,
        date TEXT NOT NULL, time TEXT NOT NULL, notes TEXT DEFAULT '',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id))''')

    conn.commit()
    c.execute('SELECT COUNT(*) FROM habits')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO habits (name, icon, target) VALUES (?, ?, ?)',
            [('Exercise', '🏃', 1), ('Water (8 glasses)', '💧', 8),
             ('Fruits (3 servings)', '🍎', 3), ('Sleep (8 hours)', '😴', 1),
             ('Meditation', '🧘', 1)])
        conn.commit()
    conn.close()

def get_all_medicines():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM medicines ORDER BY created_at DESC')
    meds = c.fetchall()
    conn.close()
    return meds

def add_medicine(name, dosage, time):
    conn = get_db()
    conn.execute('INSERT INTO medicines (name, dosage, time) VALUES (?, ?, ?)', (name, dosage, time))
    conn.commit()
    conn.close()

def mark_medicine_taken(id):
    conn = get_db()
    conn.execute('UPDATE medicines SET taken=1 WHERE id=?', (id,))
    conn.commit()
    conn.close()

def delete_medicine(id):
    conn = get_db()
    conn.execute('DELETE FROM medicines WHERE id=?', (id,))
    conn.commit()
    conn.close()

def get_today_water():
    today = date.today().isoformat()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT SUM(amount) FROM water_logs WHERE log_date=?', (today,))
    r = c.fetchone()[0]
    conn.close()
    return r if r else 0

def add_water(amount=200):
    conn = get_db()
    conn.execute('INSERT INTO water_logs (amount) VALUES (?)', (amount,))
    conn.commit()
    conn.close()

def reset_water():
    today = date.today().isoformat()
    conn = get_db()
    conn.execute('DELETE FROM water_logs WHERE log_date=?', (today,))
    conn.commit()
    conn.close()

def get_all_diary_entries():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM diary_entries ORDER BY created_at DESC')
    entries = c.fetchall()
    conn.close()
    return entries

def add_diary_entry(mood, sleep_hours, water, notes):
    conn = get_db()
    conn.execute('INSERT INTO diary_entries (mood, sleep_hours, water, notes) VALUES (?, ?, ?, ?)',
                 (mood, sleep_hours, water, notes))
    conn.commit()
    conn.close()

def delete_diary_entry(id):
    conn = get_db()
    conn.execute('DELETE FROM diary_entries WHERE id=?', (id,))
    conn.commit()
    conn.close()

MOODS = [
    {'id': 'great', 'emoji': '😄', 'label': 'Great'},
    {'id': 'good', 'emoji': '🙂', 'label': 'Good'},
    {'id': 'okay', 'emoji': '😐', 'label': 'Okay'},
    {'id': 'bad', 'emoji': '😔', 'label': 'Bad'},
    {'id': 'terrible', 'emoji': '😭', 'label': 'Terrible'},
]

def get_all_habits():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM habits ORDER BY id')
    habits = c.fetchall()
    conn.close()
    return habits

def get_habit_completions_today(habit_id):
    today = date.today().isoformat()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT completion_count FROM habit_completions WHERE habit_id=? AND completed_date=?',
              (habit_id, today))
    r = c.fetchone()
    conn.close()
    return r['completion_count'] if r else 0

def increment_habit(habit_id):
    today = date.today().isoformat()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT completion_count FROM habit_completions WHERE habit_id=? AND completed_date=?', (habit_id, today))
    existing = c.fetchone()
    if existing:
        conn.execute('UPDATE habit_completions SET completion_count=completion_count+1 WHERE habit_id=? AND completed_date=?', (habit_id, today))
    else:
        conn.execute('INSERT INTO habit_completions (habit_id, completed_date, completion_count) VALUES (?, ?, 1)', (habit_id, today))
    conn.commit()
    conn.close()

def reset_habit(habit_id):
    today = date.today().isoformat()
    conn = get_db()
    conn.execute('DELETE FROM habit_completions WHERE habit_id=? AND completed_date=?', (habit_id, today))
    conn.commit()
    conn.close()

def get_all_patients():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM patients ORDER BY created_at DESC')
    patients = c.fetchall()
    conn.close()
    return patients

def add_patient(name, phone, email=''):
    conn = get_db()
    conn.execute('INSERT INTO patients (name, phone, email) VALUES (?, ?, ?)', (name, phone, email))
    conn.commit()
    conn.close()

def get_all_appointments():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT a.*, p.name as patient_name, p.phone FROM appointments a
                 JOIN patients p ON a.patient_id=p.id ORDER BY a.date DESC''')
    apts = c.fetchall()
    conn.close()
    return apts

def add_appointment(patient_id, doctor, specialty, date_str, time_str, notes=''):
    conn = get_db()
    conn.execute('INSERT INTO appointments (patient_id, doctor, specialty, date, time, notes) VALUES (?, ?, ?, ?, ?, ?)',
                 (patient_id, doctor, specialty, date_str, time_str, notes))
    conn.commit()
    conn.close()

def delete_appointment(id):
    conn = get_db()
    conn.execute('DELETE FROM appointments WHERE id=?', (id,))
    conn.commit()
    conn.close()

DOCTORS = [
    {'name': 'Dr. Sarah Johnson', 'specialty': 'General Physician'},
    {'name': 'Dr. Michael Chen', 'specialty': 'Cardiologist'},
    {'name': 'Dr. Emily Brown', 'specialty': 'Pediatrician'},
    {'name': 'Dr. James Wilson', 'specialty': 'Orthopedic'},
]

MEDICAL_TERMS = [
    {'term': 'Cardio-', 'meaning': 'Heart', 'type': 'Prefix', 'example': 'Cardiology = Study of the heart'},
    {'term': '-itis', 'meaning': 'Inflammation', 'type': 'Suffix', 'example': 'Arthritis = Joint inflammation'},
    {'term': 'Gastro-', 'meaning': 'Stomach', 'type': 'Prefix', 'example': 'Gastroenteritis = Stomach inflammation'},
    {'term': '-ectomy', 'meaning': 'Surgical removal', 'type': 'Suffix', 'example': 'Appendectomy = Removal of appendix'},
    {'term': 'Neuro-', 'meaning': 'Nerve', 'type': 'Prefix', 'example': 'Neurology = Study of nerves'},
    {'term': '-osis', 'meaning': 'Abnormal condition', 'type': 'Suffix', 'example': 'Neurosis = Nerve abnormality'},
    {'term': 'Dermato-', 'meaning': 'Skin', 'type': 'Prefix', 'example': 'Dermatitis = Skin inflammation'},
    {'term': '-emia', 'meaning': 'Blood condition', 'type': 'Suffix', 'example': 'Anemia = Blood deficiency'},
    {'term': 'Osteo-', 'meaning': 'Bone', 'type': 'Prefix', 'example': 'Osteoporosis = Bone porosity'},
    {'term': '-ology', 'meaning': 'Study of', 'type': 'Suffix', 'example': 'Psychology = Study of the mind'},
    {'term': 'Pulmo-', 'meaning': 'Lung', 'type': 'Prefix', 'example': 'Pulmonary = Related to lungs'},
    {'term': '-pathy', 'meaning': 'Disease', 'type': 'Suffix', 'example': 'Neuropathy = Nerve disease'},
    {'term': 'Hepato-', 'meaning': 'Liver', 'type': 'Prefix', 'example': 'Hepatitis = Liver inflammation'},
    {'term': '-megaly', 'meaning': 'Enlargement', 'type': 'Suffix', 'example': 'Cardiomegaly = Enlarged heart'},
    {'term': 'Cephalo-', 'meaning': 'Head', 'type': 'Prefix', 'example': 'Encephalitis = Brain inflammation'},
    {'term': '-rrhea', 'meaning': 'Discharge', 'type': 'Suffix', 'example': 'Diarrhea = Excessive bowel discharge'},
    {'term': 'Arthro-', 'meaning': 'Joint', 'type': 'Prefix', 'example': 'Arthritis = Joint inflammation'},
    {'term': '-plasty', 'meaning': 'Surgical repair', 'type': 'Suffix', 'example': 'Rhinoplasty = Nose reconstruction'},
    {'term': 'Reno-', 'meaning': 'Kidney', 'type': 'Prefix', 'example': 'Renovascular = Related to kidney vessels'},
    {'term': '-tomy', 'meaning': 'Incision', 'type': 'Suffix', 'example': 'Appendectomy = Cutting into appendix'},
]

FIRST_AID = [
    {'id': 'burns', 'title': 'Burns', 'icon': '🔥', 'steps': [
        'Cool the burn: Run cool water for 10-20 minutes',
        'Remove jewelry/clothing before swelling',
        'Do not break blisters',
        'Apply aloe vera for minor burns',
        'Cover with sterile non-stick bandage',
        'Take OTC pain medication if needed'
    ], 'warnings': ['Do NOT use ice', 'Do NOT use butter', 'Seek help for large burns']},
    {'id': 'cuts', 'title': 'Cuts & Wounds', 'icon': '🩹', 'steps': [
        'Stop bleeding: Apply pressure with clean cloth',
        'Clean wound with clean water for 5 minutes',
        'Remove any debris gently',
        'Apply antibiotic ointment',
        'Cover with sterile bandage',
        'Change dressing daily'
    ], 'warnings': ['Seek help if bleeding does not stop', 'Seek help if wound is deep']},
    {'id': 'nosebleeds', 'title': 'Nosebleeds', 'icon': '🩸', 'steps': [
        'Sit upright and lean forward',
        'Pinch soft part of nose',
        'Breathe through mouth',
        'Hold for 10-15 minutes',
        'Apply ice to bridge of nose',
        'Avoid blowing nose for hours'
    ], 'warnings': ['Do NOT lean back', 'Seek help if longer than 20 minutes']},
    {'id': 'sprains', 'title': 'Sprains', 'icon': '🦾', 'steps': [
        'Rest the injured area',
        'Ice for 15-20 minutes',
        'Compress with elastic bandage',
        'Elevate above heart level',
        'Take anti-inflammatory meds',
        'Use brace for support'
    ], 'warnings': ['Seek help if cannot bear weight', 'Could be fracture']},
    {'id': 'choking', 'title': 'Choking', 'icon': '😮', 'steps': [
        'Ask if choking - if coughing, encourage it',
        'Call 911 if severe',
        '5 firm back blows',
        '5 Heimlich abdominal thrusts',
        'Alternate until clear',
        'Begin CPR if unconscious'
    ], 'warnings': ['For infants: use chest thrusts', 'Check for internal injuries after']},
    {'id': 'heat', 'title': 'Heat Exhaustion', 'icon': '☀️', 'steps': [
        'Move to cool area immediately',
        'Hydrate with cool water',
        'Apply cool wet cloths to skin',
        'Use fan while misting',
        'Apply ice packs to neck/armpits/groin',
        'Monitor for 30 minutes'
    ], 'warnings': ['Call 911 if symptoms of heatstroke']},
]

STRETCHES = [
    {'title': 'Neck Release', 'instruction': 'Slowly tilt head to one side, hold 15 seconds, switch sides. Relieves neck tension.'},
    {'title': 'Seated Twist', 'instruction': 'Sit upright, place right hand on left knee, twist gently. Hold 15 sec, switch.'},
    {'title': 'Wrist Extension', 'instruction': 'Extend arm palm up, pull fingers down with other hand. Hold 15 sec per side.'},
    {'title': 'Shoulder Shrugs', 'instruction': 'Raise shoulders to ears, hold 5 seconds, release. Repeat 10 times.'},
    {'title': 'Eye Rest', 'instruction': 'Follow 20-20-20 rule: Look at something 20 feet away for 20 seconds.'},
]