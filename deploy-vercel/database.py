import os
import json
import tempfile
from datetime import date, datetime

DATA_FILE = os.path.join(tempfile.gettempdir(), 'vitalcore_data.json')

def _now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def _empty():
    return {
        'medicines': [], 'water_logs': [], 'diary_entries': [],
        'habits': [], 'habit_completions': [], 'patients': [], 'appointments': [],
        'seq': {'medicines': 1, 'water_logs': 1, 'diary_entries': 1, 'habits': 1,
                'habit_completions': 1, 'patients': 1, 'appointments': 1},
    }

def _load():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return _empty()

def _save(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def _next(data, key):
    nid = data['seq'][key]
    data['seq'][key] = nid + 1
    return nid

def init_db():
    data = _load()
    if not data.get('habits'):
        data['habits'] = [
            {'id': 1, 'name': 'Exercise', 'icon': '🏃', 'target': 1},
            {'id': 2, 'name': 'Water (8 glasses)', 'icon': '💧', 'target': 8},
            {'id': 3, 'name': 'Fruits (3 servings)', 'icon': '🍎', 'target': 3},
            {'id': 4, 'name': 'Sleep (8 hours)', 'icon': '😴', 'target': 1},
            {'id': 5, 'name': 'Meditation', 'icon': '🧘', 'target': 1},
        ]
        data['seq']['habits'] = 6
    _save(data)

def get_all_medicines():
    data = _load()
    meds = sorted(data['medicines'], key=lambda m: m['created_at'], reverse=True)
    return meds

def add_medicine(name, dosage, time):
    data = _load()
    data['medicines'].append({
        'id': _next(data, 'medicines'), 'name': name, 'dosage': dosage,
        'time': time, 'taken': 0, 'created_at': _now(),
    })
    _save(data)

def mark_medicine_taken(id):
    data = _load()
    for m in data['medicines']:
        if m['id'] == id:
            m['taken'] = 1
    _save(data)

def delete_medicine(id):
    data = _load()
    data['medicines'] = [m for m in data['medicines'] if m['id'] != id]
    _save(data)

def get_today_water():
    today = date.today().isoformat()
    data = _load()
    return sum(w['amount'] for w in data['water_logs'] if w['log_date'] == today)

def add_water(amount=200):
    data = _load()
    data['water_logs'].append({
        'id': _next(data, 'water_logs'), 'amount': amount,
        'log_date': date.today().isoformat(),
    })
    _save(data)

def reset_water():
    today = date.today().isoformat()
    data = _load()
    data['water_logs'] = [w for w in data['water_logs'] if w['log_date'] != today]
    _save(data)

def get_all_diary_entries():
    data = _load()
    entries = sorted(data['diary_entries'], key=lambda e: e['created_at'], reverse=True)
    return entries

def add_diary_entry(mood, sleep_hours, water, notes):
    data = _load()
    data['diary_entries'].append({
        'id': _next(data, 'diary_entries'), 'mood': mood, 'sleep_hours': sleep_hours,
        'water': water, 'notes': notes, 'created_at': _now(),
    })
    _save(data)

def delete_diary_entry(id):
    data = _load()
    data['diary_entries'] = [e for e in data['diary_entries'] if e['id'] != id]
    _save(data)

MOODS = [
    {'id': 'great', 'emoji': '😄', 'label': 'Great'},
    {'id': 'good', 'emoji': '🙂', 'label': 'Good'},
    {'id': 'okay', 'emoji': '😐', 'label': 'Okay'},
    {'id': 'bad', 'emoji': '😔', 'label': 'Bad'},
    {'id': 'terrible', 'emoji': '😭', 'label': 'Terrible'},
]

def get_all_habits():
    data = _load()
    return sorted(data['habits'], key=lambda h: h['id'])

def get_habit_completions_today(habit_id):
    today = date.today().isoformat()
    data = _load()
    for c in data['habit_completions']:
        if c['habit_id'] == habit_id and c['completed_date'] == today:
            return c['completion_count']
    return 0

def increment_habit(habit_id):
    today = date.today().isoformat()
    data = _load()
    for c in data['habit_completions']:
        if c['habit_id'] == habit_id and c['completed_date'] == today:
            c['completion_count'] += 1
            _save(data)
            return
    data['habit_completions'].append({
        'id': _next(data, 'habit_completions'), 'habit_id': habit_id,
        'completed_date': today, 'completion_count': 1,
    })
    _save(data)

def reset_habit(habit_id):
    today = date.today().isoformat()
    data = _load()
    data['habit_completions'] = [
        c for c in data['habit_completions']
        if not (c['habit_id'] == habit_id and c['completed_date'] == today)
    ]
    _save(data)

def get_all_patients():
    data = _load()
    return sorted(data['patients'], key=lambda p: p['created_at'], reverse=True)

def add_patient(name, phone, email=''):
    data = _load()
    data['patients'].append({
        'id': _next(data, 'patients'), 'name': name, 'phone': phone,
        'email': email, 'created_at': _now(),
    })
    _save(data)

def get_all_appointments():
    data = _load()
    patients = {p['id']: p for p in data['patients']}
    apts = []
    for a in data['appointments']:
        p = patients.get(a['patient_id'], {})
        apts.append({
            'id': a['id'], 'patient_id': a['patient_id'], 'doctor': a['doctor'],
            'specialty': a['specialty'], 'date': a['date'], 'time': a['time'],
            'notes': a['notes'], 'created_at': a['created_at'],
            'patient_name': p.get('name', 'Unknown'), 'phone': p.get('phone', ''),
        })
    return sorted(apts, key=lambda a: a['created_at'], reverse=True)

def add_appointment(patient_id, doctor, specialty, date_str, time_str, notes=''):
    data = _load()
    data['appointments'].append({
        'id': _next(data, 'appointments'), 'patient_id': patient_id, 'doctor': doctor,
        'specialty': specialty, 'date': date_str, 'time': time_str,
        'notes': notes, 'created_at': _now(),
    })
    _save(data)

def delete_appointment(id):
    data = _load()
    data['appointments'] = [a for a in data['appointments'] if a['id'] != id]
    _save(data)

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