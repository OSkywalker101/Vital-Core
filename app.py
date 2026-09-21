from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    init_db, get_all_medicines, add_medicine, mark_medicine_taken, delete_medicine,
    get_today_water, add_water, reset_water,
    get_all_diary_entries, add_diary_entry, delete_diary_entry, MOODS,
    get_all_habits, get_habit_completions_today, increment_habit, reset_habit,
    get_all_patients, add_patient, get_all_appointments, add_appointment, delete_appointment, DOCTORS,
    MEDICAL_TERMS, FIRST_AID, STRETCHES
)
import socket, random

app = Flask(__name__)
app.secret_key = 'vitalcore-secret-2024'
DAILY_WATER_GOAL = 2000

def find_port(start=5001, end=5020):
    for p in range(start, end):
        try:
            s = socket.socket()
            s.bind(('', p))
            s.close()
            return p
        except:
            continue
    return start

@app.template_filter('dt')
def dt_filter(v):
    if v: return v[:16]
    return ''

@app.route('/')
def dashboard():
    water = get_today_water()
    wp = min(int((water / DAILY_WATER_GOAL) * 100), 100)
    meds = get_all_medicines()
    habits = get_all_habits()
    total_prog = 0
    done_habits = 0
    for h in habits:
        cur = get_habit_completions_today(h['id'])
        prog = min(int((cur / h['target']) * 100), 100)
        total_prog += prog
        if cur >= h['target']: done_habits += 1
    habit_avg = int(total_prog / len(habits)) if habits else 0
    return render_template('dashboard.html',
        water=water, water_glasses=water//200, water_pct=wp,
        medicine_count=len([m for m in meds if not m['taken']]),
        appointment_count=len(get_all_appointments()),
        habit_avg=habit_avg, done_habits=done_habits, total_habits=len(habits))

# --- MEDICINE ---
@app.route('/medicine')
def medicine():
    return render_template('medicine.html', medicines=get_all_medicines())

@app.route('/medicine/add', methods=['POST'])
def medicine_add():
    n, d, t = request.form.get('name'), request.form.get('dosage'), request.form.get('time')
    if n and d and t:
        add_medicine(n, d, t)
        flash(f'{n} added! 💊', 'success')
    return redirect(url_for('medicine'))

@app.route('/medicine/taken/<int:id>')
def medicine_taken(id):
    mark_medicine_taken(id)
    flash('Marked as taken! ✅', 'success')
    return redirect(url_for('medicine'))

@app.route('/medicine/delete/<int:id>')
def medicine_delete(id):
    delete_medicine(id)
    flash('Medicine deleted! 🗑️', 'danger')
    return redirect(url_for('medicine'))

# --- BMI ---
@app.route('/bmi')
def bmi():
    return render_template('bmi.html')

# --- SYMPTOM ---
SYMPTOM_RULES = {
    ('fever', 'cough'): ('Flu', 'Rest, fluids, see doctor if worsens'),
    ('fever', 'headache'): ('Viral Fever', 'Rest, hydration, see doctor if fever >103°F'),
    ('cough', 'sore_throat'): ('Common Cold', 'Rest, warm fluids, honey'),
    ('fever',): ('Mild Fever', 'Rest, stay hydrated'),
    ('cough',): ('Mild Cough', 'Stay hydrated, avoid irritants'),
    ('headache',): ('General Headache', 'Rest, hydration, pain relievers'),
    ('stomach_pain',): ('Stomach Ache', 'Rest, light foods, warm fluids'),
}

SYMPTOMS = [
    {'id': 'fever', 'name': 'Fever', 'icon': '🌡️'},
    {'id': 'cough', 'name': 'Cough', 'icon': '😷'},
    {'id': 'headache', 'name': 'Headache', 'icon': '🤕'},
    {'id': 'body_ache', 'name': 'Body Ache', 'icon': '💪'},
    {'id': 'sore_throat', 'name': 'Sore Throat', 'icon': '🗣️'},
    {'id': 'stomach_pain', 'name': 'Stomach Pain', 'icon': '🤢'},
]

@app.route('/symptom')
def symptom():
    return render_template('symptom.html', symptoms=SYMPTOMS)

@app.route('/symptom/check', methods=['POST'])
def symptom_check():
    sel = request.form.getlist('symptoms')
    if not sel:
        flash('Select at least one symptom', 'warning')
        return redirect(url_for('symptom'))
    result = None
    for s_key, res in SYMPTOM_RULES.items():
        if all(s in sel for s in s_key):
            result = {'condition': res[0], 'advice': res[1],
                      'matched': list(s_key), 'selected': sel}
            break
    if not result:
        result = {'condition': 'Unknown', 'advice': 'Consult a healthcare professional',
                  'matched': [], 'selected': sel}
    return render_template('symptom.html', symptoms=SYMPTOMS, result=result, selected=sel)

# --- WATER ---
@app.route('/water')
def water():
    w = get_today_water()
    return render_template('water.html', water=w, glasses=w//200, pct=min(int((w/DAILY_WATER_GOAL)*100),100))

@app.route('/water/add', methods=['POST'])
def water_add():
    add_water(200)
    flash('Water added! 💧', 'success')
    return redirect(url_for('water'))

@app.route('/water/reset', methods=['POST'])
def water_reset():
    reset_water()
    flash('Water reset! 🔄', 'info')
    return redirect(url_for('water'))

# --- FIRST AID ---
@app.route('/firstaid')
def firstaid():
    q = request.args.get('q', '').lower()
    topics = FIRST_AID
    if q:
        topics = [t for t in topics if q in t['title'].lower()]
    return render_template('firstaid.html', topics=topics)

# --- DIARY ---
@app.route('/diary')
def diary():
    return render_template('diary.html', entries=get_all_diary_entries(), moods=MOODS)

@app.route('/diary/add', methods=['POST'])
def diary_add():
    m = request.form.get('mood')
    if m:
        add_diary_entry(m, float(request.form.get('sleep', 0)),
                        int(request.form.get('water', 0)), request.form.get('notes', ''))
        flash('Entry saved! 📝', 'success')
    return redirect(url_for('diary'))

@app.route('/diary/delete/<int:id>')
def diary_delete(id):
    delete_diary_entry(id)
    flash('Entry deleted! 🗑️', 'danger')
    return redirect(url_for('diary'))

# --- HABITS ---
@app.route('/habit')
def habit():
    hb = get_all_habits()
    hd = []
    total = 0
    for h in hb:
        cur = get_habit_completions_today(h['id'])
        prog = min(int((cur / h['target']) * 100), 100)
        hd.append({'id': h['id'], 'name': h['name'], 'icon': h['icon'],
                    'target': h['target'], 'current': cur, 'progress': prog,
                    'done': cur >= h['target']})
        total += prog
    avg = int(total / len(hd)) if hd else 0
    return render_template('habit.html', habits=hd, avg=avg)

@app.route('/habit/inc/<int:id>')
def habit_inc(id):
    increment_habit(id)
    return redirect(url_for('habit'))

@app.route('/habit/reset/<int:id>')
def habit_reset(id):
    reset_habit(id)
    return redirect(url_for('habit'))

# --- APPOINTMENTS ---
@app.route('/appointment')
def appointment():
    return render_template('appointment.html',
        appointments=get_all_appointments(),
        patients=get_all_patients(),
        doctors=DOCTORS)

@app.route('/appointment/register', methods=['POST'])
def appointment_register():
    n, p = request.form.get('name'), request.form.get('phone')
    if n and p:
        add_patient(n, p, request.form.get('email', ''))
        flash(f'Patient {n} registered! 🎉', 'success')
    return redirect(url_for('appointment'))

@app.route('/appointment/book', methods=['POST'])
def appointment_book():
    if all(request.form.get(x) for x in ['patient_id', 'doctor', 'date', 'time']):
        add_appointment(request.form.get('patient_id'), request.form.get('doctor'),
                       request.form.get('specialty', ''), request.form.get('date'),
                       request.form.get('time'), request.form.get('notes', ''))
        flash(f'Appointment with {request.form.get("doctor")} booked! 📅', 'success')
    return redirect(url_for('appointment'))

@app.route('/appointment/cancel/<int:id>')
def appointment_cancel(id):
    delete_appointment(id)
    flash('Appointment cancelled! 🗑️', 'info')
    return redirect(url_for('appointment'))

# --- VISION ---
@app.route('/vision')
def vision():
    return render_template('vision.html')

# --- QUIZ ---
@app.route('/quiz')
def quiz():
    return render_template('quiz.html', terms=MEDICAL_TERMS)

# --- CONVERTER ---
@app.route('/converter')
def converter():
    return render_template('converter.html')

# --- HEARING ---
@app.route('/hearing')
def hearing():
    return render_template('hearing.html')

# --- STRETCH ---
@app.route('/stretch')
def stretch():
    cs = random.choice(STRETCHES)
    return render_template('stretch.html', stretches=STRETCHES, current=cs)

if __name__ == '__main__':
    init_db()
    port = find_port()
    print(f"\n{'='*50}")
    print(f"🏥 VITALCORE starting on http://localhost:{port}")
    print(f"📁 VITAL Information & Tracking for Assessing Life")
    print(f"✅ 13 Features: Medicine, Water, Diary, Habits, BMI,")
    print(f"   Symptom, First Aid, Appointments, Vision,")
    print(f"   Quiz, Converter, Hearing, Stretch")
    print(f"{'='*50}\n")
    app.run(debug=True, port=port)