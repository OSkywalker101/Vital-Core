# 🏥 VITALCORE

**V**ital **I**nformation & **T**racking for **A**ssessing **L**ife

A comprehensive, all-in-one health companion web application combining **13 health tools** into a single beautifully designed Flask application.

## ✨ Features (13 Tools)

### Health Tracking (4)
- 💊 **Medicine Reminder** - Track medications, dosages, schedules
- 💧 **Water Tracker** - Monitor daily water intake with progress ring
- 🩹 **Health Diary** - Log mood, sleep, water, notes
- 🌼 **Habit Tracker** - Build healthy habits with streaks

### Health Tools (4)
- 🩺 **BMI Calculator** - Real-time BMI with health categories
- 🌸 **Symptom Checker** - Basic symptom-to-condition matching
- 🧸 **First Aid Guide** - Searchable emergency instructions
- ⚕️ **Unit Converter** - Medical conversions (blood sugar, weight, temp)

### Wellness Tests (4)
- 👁️ **Vision Test** - Snellen E-chart visual acuity test
- 📝 **Med Quiz** - Flashcard-based medical terminology
- 🔊 **Hearing Test** - Web Audio frequency range test
- ⏱️ **Stretch Timer** - 2-minute desk stretch countdown

### Appointments (1)
- 🐻 **Hospital Appointments** - Patient registration & booking

## 🚀 Quick Start

```bash
cd vitalcore
pip install -r requirements.txt
python app.py
```

The app auto-detects an available port (starting at 5001) and prints the URL.

## 📁 Project Structure

```
vitalcore/
├── app.py              # Flask routes (all 13 features)
├── database.py         # SQLite schema + data
├── requirements.txt    # flask==3.0.0
├── templates/
│   ├── layout.html     # Sidebar navigation
│   ├── dashboard.html   # Home overview
│   ├── medicine.html   # Medicine tracker
│   ├── water.html      # Water tracker
│   ├── diary.html      # Health diary
│   ├── habit.html      # Habit tracker
│   ├── bmi.html        # BMI calculator
│   ├── symptom.html    # Symptom checker
│   ├── firstaid.html   # First aid guide
│   ├── appointment.html # Appointment booking
│   ├── vision.html     # Vision test
│   ├── quiz.html       # Medical quiz
│   ├── converter.html  # Unit converter
│   ├── hearing.html    # Hearing test
│   └── stretch.html    # Stretch timer
└── instance/
    └── vitalcore.db   # SQLite (auto-created)
```

## 🎨 Design

- **Theme:** Soft pastel medical aesthetic
- **Sidebar:** Fixed navigation with 13 feature icons
- **Font:** Nunito (friendly, rounded)
- **Responsive:** Desktop and mobile-friendly
- **Animations:** Smooth transitions and hover effects

## 🗄️ Database

Single SQLite database with 7 tables:
- `medicines` - name, dosage, time, taken
- `water_logs` - amount, date
- `diary_entries` - mood, sleep, water, notes
- `habits` + `habit_completions` - habit tracking with streaks
- `patients` + `appointments` - patient management

## 🔧 Tech Stack

- **Backend:** Flask 3.0 (Python)
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Styling:** Tailwind CSS (CDN)
- **Dependencies:** Flask only (no other packages)

## ⚠️ Disclaimer

For **educational and demonstration purposes only**. Medical information provided should not be used as a substitute for professional medical advice.

## 🎯 Perfect For

- College presentations
- Health science projects
- Portfolio demonstration
- Learning Flask web development

---

**VITALCORE** - Your complete health companion! 🏥💚