<div align="center">

# Scoliosis Brace Coach AI

**AI-powered posture monitoring that helps avoid unnecessary surgery**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Tasks-FF6F00?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A web application that uses computer vision to analyze posture from photos and videos,
track scoliosis treatment progress, and generate clinical reports — running entirely
on your local machine with no cloud dependency.

**Created by [Srinath Sankara](https://github.com/srinathsankara)**

> **Important Medical Disclaimer** — This application is designed to help parents and
> caregivers monitor scolosis treatment progress between clinical visits. It is **not**
> a medical device, does **not** provide medical diagnosis, and does **not** replace
> professional medical advice, diagnosis, or treatment. Always seek the advice of your
> physician or other qualified health provider with any questions regarding a medical
> condition. Never disregard professional medical advice or delay in seeking it because
> of something you have read or seen in this application. The author assumes no
> responsibility or liability for any errors or omissions in the content of this
> application. Use of this application is entirely at your own risk.

[What is this?](#what-is-this) | [Who is this for?](#who-is-this-for) | [Quick Start](#quick-start) | [How to Use](#how-to-use) | [Features](#features) | [For Developers](#for-developers)

</div>

---

## Table of Contents

- [What is this?](#what-is-this)
- [Who is this for?](#who-is-this-for)
- [Quick Start](#quick-start)
- [How to Use](#how-to-use)
- [Features](#features)
- [How It Works](#how-it-works)
- [For Developers](#for-developers)
- [API Reference](#api-reference)
- [Clinical Background](#clinical-background)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## What is this?

Scoliosis Brace Coach AI is a tool that helps families and clinicians monitor scoliosis treatment between office visits. It answers three critical questions:

1. **Is the brace actually working?** — Measures how much posture improves when wearing the brace
2. **Is the curve getting worse?** — Tracks asymmetry over time and alerts when progression is detected
3. **Is the brace being worn enough?** — Logs wear-time and pressure distribution

### The Problem It Solves

Adolescent Idiopathic Scoliosis (AIS) affects **2-3% of adolescents**. The standard treatment is bracing combined with physical therapy (Schroth method). But there's a gap:

- Clinic visits happen every **4-6 months**
- Curves can progress **1-2 degrees per month** during growth
- By the time progression is noticed at a clinic visit, it may be too late to avoid surgery
- Spinal fusion surgery costs **$100,000–$300,000** and permanently limits mobility

This tool fills that gap by giving families **objective, quantitative data** at home — so problems are caught early and treatment can be adjusted before surgery becomes necessary.

### The Evidence

The landmark **BrAIST trial** (New England Journal of Medicine, 2013) proved:
- Bracing reduces the risk of surgery by **72%**
- The more hours per day the brace is worn, the better the outcome
- **13+ hours/day** showed a 90% success rate

This tool helps families achieve those compliance numbers by making progress visible and measurable.

---

## Who is this for?

### For Patients and Parents

> "I want to know if the brace is actually helping my child."

- Upload a photo after each brace fitting to see exactly how much correction is being achieved
- Track posture improvement week by week with easy-to-read charts
- Get alerted if metrics worsen — before the next scheduled clinic visit
- Download PDF reports to bring to orthopedic appointments
- Stay motivated by seeing measurable progress

### For Orthopedic Specialists and Orthotists

> "I need objective data to make better treatment decisions."

- Review patient data remotely through the clinician dashboard
- See brace pressure distribution to verify corrective force at the curve apex
- Identify patients with progression alerts who need urgent attention
- Export clinical-grade PDF reports for documentation and insurance
- Make data-driven decisions about brace adjustments vs. surgical referral

### For Physical Therapists (Schroth-Certified)

> "I need to verify my patients are doing their exercises correctly."

- Monitor exercise form between in-person sessions
- Track posture metrics to validate treatment effectiveness
- Compare with-brace vs. without-brace sessions to demonstrate brace value
- Use trend data to adjust exercise programs

---

## Quick Start

### Prerequisites

- **Python 3.11** or higher ([download Python](https://www.python.org/downloads/))
- **pip** (comes with Python)
- A webcam or smartphone camera

### Installation

**Option 1: Automatic (Windows)**

```bash
git clone https://github.com/yourusername/scoliosis-brace-coach.git
cd scoliosis-brace-coach
install.bat
```

**Option 2: Manual (All Platforms)**

```bash
git clone https://github.com/yourusername/scoliosis-brace-coach.git
cd scoliosis-brace-coach
pip install -r requirements.txt
```

### Running the Application

```bash
python app.py
```

Or on Windows, double-click `start.bat`.

Then open your browser to: **http://127.0.0.1:5000**

> **First run note:** The application will automatically download the AI pose detection model (~5 MB) from Google Cloud Storage. This only happens once.

---

## How to Use

### Step 1: Take a Photo or Video

Stand or walk directly facing away from the camera (posterior view). The person's **entire body** should be visible from head to ankles.

**Good photo:**
- Person centered in frame, facing away from camera
- Good lighting, plain background
- Fitted clothing so body contours are visible

**Bad photo:**
- Person facing the camera or at an angle
- Shadows or cluttered background
- Loose clothing hiding body shape

### Step 2: Upload and Select Options

1. Click **Choose File** and select your photo or video
2. Select the **Session Type**:
   - Standing (Without Brace) — baseline measurement
   - Standing (With Brace) — measures brace correction
   - Walking (Without Brace) — gait analysis
   - Walking (With Brace) — braced gait analysis
   - Schroth Exercise — exercise form check
3. Select the **Age Group** (Under 12, Under 15, Under 18, or Adult)
4. Click **Analyze Session**

### Step 3: Review Results

The analysis typically takes **2-5 seconds**. Results include:

- **Shoulder Asymmetry** — Height difference between left and right shoulders (pixels)
- **Hip Asymmetry** — Height difference between left and right hips (pixels)
- **Trunk Lean Angle** — How much the torso tilts to one side (degrees)
- **Head Tilt** — How far the head deviates from center (pixels)
- **Spine Deviation** — Lateral shift of the spine (pixels)
- **Trunk Rotation** — Estimated vertebral rotation (degrees)
- **Rib Hump Proxy** — Estimated rib prominence asymmetry (pixels)
- **Rotation Risk Score** — Composite score from 0-100 (higher = worse)

Each metric shows a **status badge**: green for good, yellow for needs improvement.

### Step 4: Compare Sessions

Go to **Compare Sessions** to see side-by-side how the brace improves posture. This is the most powerful feature — it shows exactly how many degrees of correction the brace provides.

### Step 5: Track Trends

Go to **Trends** to see charts of all metrics over time. The system automatically detects:
- **Stable** — metrics are consistent (good!)
- **Improving** — asymmetry is decreasing (treatment working)
- **Worsening** — asymmetry is increasing (may need attention)

### Step 6: Export Reports

Go to **Clinician Dashboard** and click **Export PDF** to download a clinical-grade report with:
- Session summary
- Brace effectiveness percentage
- Longitudinal trend analysis
- Progression alerts
- Evidence-based treatment rationale
- Recommendations

Bring this PDF to your next orthopedic appointment.

---

## Features

### Core Analysis

| Feature | What It Measures | Why It Matters |
|---|---|---|
| **Pose Estimation** | 33 body landmarks from a single photo | Foundation for all other measurements |
| **Posture Metrics** | Shoulder, hip, trunk, head, spine asymmetry | Primary indicators of scoliosis severity |
| **Rotation Detection** | Trunk rotation, rib hump, pelvic obliquity | Scoliosis is 3D — rotation matters as much as lateral curve |
| **Brace Detection** | Whether a brace is present in the image | Automatically categorizes with/without brace sessions |
| **Gait Analysis** | Pelvic tilt, step symmetry during walking | Walking patterns reveal functional impact |

### Treatment Monitoring

| Feature | What It Does | Why It Matters |
|---|---|---|
| **Session Comparison** | Side-by-side with/without brace analysis | Proves the brace is actually correcting posture |
| **Trend Analysis** | Linear regression across all sessions | Detects slow progression that single snapshots miss |
| **Progression Alerts** | Critical/warning alerts at clinical thresholds | Early warning before curve crosses surgical threshold |
| **Age-Specific Thresholds** | Different standards for under 12/15/18/adult | Growing spines have different risk profiles |

### Brace Intelligence

| Feature | What It Does | Why It Matters |
|---|---|---|
| **Pressure Evaluation** | Scores force at 3 correction points | Verifies brace applies force at the curve apex |
| **Compliance Tracking** | Logs wear-time via temperature detection | 13+ hours/day = 90% success rate (BrAIST) |
| **Pressure History** | Time-series of pressure readings | Shows if brace fit changes over time |

### Clinical Tools

| Feature | What It Does | Why It Matters |
|---|---|---|
| **Clinician Dashboard** | KPIs, alerts, trend overview | At-a-glance view of patient status |
| **PDF Reports** | A4 clinical reports with evidence citations | Ready for doctor visits and insurance |
| **Educational Content** | AIS treatment evidence and surgery prevention | Helps families understand the importance of compliance |

---

## How It Works

### The Analysis Pipeline

```
Photo/Video Upload
       │
       ▼
┌──────────────────┐
│  File Validation  │  Check extension, size (max 500MB)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Frame Sampling   │  Videos: extract 10 evenly-spaced frames
│                   │  Images: use directly
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│  MediaPipe Pose   │────▶│  33 Body         │  Normalized (x,y,z) coordinates
│  Landmark Detect  │     │  Landmarks       │  for each landmark
└────────┬─────────┘     └─────────────────┘
         │
         ▼
┌──────────────────┐
│  Brace Detection  │  HSV color analysis on torso region
│  (if applicable)  │  White pixels > 20% = brace present
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Metric Compute   │  6 posture + 6 rotation metrics
│  (age-adjusted)   │  Thresholds vary by age group
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Store & Display  │  Save to SQLite, render results page
└──────────────────┘
```

### Metric Computation

**Posture Metrics** (from `posture_rules.py`):

| Metric | Calculation | Units |
|---|---|---|
| Shoulder Asymmetry | `\|left_shoulder_Y - right_shoulder_Y\|` | pixels |
| Hip Asymmetry | `\|left_hip_Y - right_hip_Y\|` | pixels |
| Trunk Lean Angle | `arctan2(mid_shoulder_X - mid_hip_X, mid_hip_Y - mid_shoulder_Y)` | degrees |
| Head Tilt | `nose_X - mid_shoulder_X` | pixels |
| Spine Deviation | `mid_shoulder_X - mid_hip_X` | pixels |
| Arm Hang Diff | `\|(left_shoulder_Y - left_wrist_Y) - (right_shoulder_Y - right_wrist_Y)\|` | pixels |

**Rotation Metrics** (from `rotation_rules.py`):

| Metric | Calculation | Units |
|---|---|---|
| Rib Hump Proxy | `\|left_shoulder_width - right_shoulder_width\|` | pixels |
| Axillary Fold Diff | `\|left_elbow_Y - right_elbow_Y\|` | pixels |
| Trunk Rotation Angle | `\|shoulder_line_angle - hip_line_angle\|` | degrees |
| Scapular Winging Diff | `\|left_scapular_dist - right_scapular_dist\|` | pixels |
| Pelvic Obliquity | `\|left_hip_Y - right_hip_Y\|` | pixels |
| Rotation Risk Score | Weighted composite (0-100) | score |

### Age-Group Thresholds

Metrics are compared against age-specific thresholds. What's "normal" for a 10-year-old is different from an adult:

| Metric | Under 12 | Under 15 | Under 18 | Adult |
|---|---|---|---|---|
| Shoulder Asymmetry | 12 px | 15 px | 18 px | 20 px |
| Trunk Lean Angle | 2.5° | 3.0° | 3.5° | 4.0° |
| Rib Hump | 5 px | 7 px | 9 px | 10 px |
| Axillary Fold | 4 px | 5 px | 6 px | 7 px |
| Rotation Angle | 3° | 4° | 5° | 5° |

### Progression Alerts

The system uses linear regression to detect trends across sessions:

| Alert Level | Trigger | Meaning |
|---|---|---|
| **Critical** | Metric changes by ≥ threshold | Significant progression — consult specialist |
| **Warning** | Metric changes by ≥ threshold | Worsening trend — schedule follow-up |
| **Stable** | Slope < 0.1 | No significant change (good!) |

---

## For Developers

### Architecture

```
scoliosis-brace-coach/
│
├── app.py                          # Flask application (routes, job management, DB init)
│
├── analysis/                       # Core analysis engine
│   ├── pose_detector.py            # MediaPipe PoseLandmarker wrapper
│   ├── video_processor.py          # Orchestrates the full analysis pipeline
│   ├── brace_detector.py           # HSV color-space brace presence detection
│   ├── posture_rules.py            # 6 standing posture metrics + thresholds
│   ├── rotation_rules.py           # 6 rotation/rib hump metrics + risk score
│   ├── gait_rules.py               # Walking gait analysis (minimal)
│   ├── exercise_rules.py           # Schroth exercise form (placeholder)
│   ├── trend_analysis.py           # Linear regression, alerts, progression reports
│   └── clinician_report.py         # PDF generation with ReportLab
│
├── sensors/                        # Hardware integration
│   ├── ble_scanner.py              # Bluetooth LE device scanning (Bleak)
│   └── brace_pressure.py           # Pressure evaluation, compliance tracking
│
├── templates/                      # Jinja2 HTML templates
│   ├── index.html                  # Home page with upload form
│   ├── results.html                # Analysis results display
│   ├── dashboard.html              # Clinician dashboard
│   ├── history.html                # Session history
│   ├── compare.html                # Side-by-side comparison
│   ├── sensors.html                # Sensor pairing & pressure input
│   ├── trends.html                 # Longitudinal trend charts
│   └── about.html                  # AIS educational content
│
├── static/
│   ├── css/style.css               # Custom styles
│   └── js/compare.js               # Client-side comparison logic
│
├── requirements.txt                # Python dependencies
├── install.bat                     # Windows installer
├── start.bat                       # Windows launcher
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

### Tech Stack

| Component | Technology | Version |
|---|---|---|
| Language | Python | 3.11+ |
| Web Framework | Flask | ≥ 2.3.0 |
| ML/CV Runtime | Google MediaPipe Tasks | ≥ 0.10.0 |
| Image Processing | OpenCV | ≥ 4.8.0 |
| Numerical | NumPy | ≥ 1.24.0 |
| PDF Generation | ReportLab | ≥ 4.0.0 |
| BLE (optional) | Bleak | ≥ 0.21.0 |
| Database | SQLite | built-in |
| Frontend CSS | Tailwind CSS | CDN |
| Frontend Charts | Chart.js | CDN |

### Database Schema

**`sessions.db`** — Analysis session results

```sql
CREATE TABLE sessions (
    job_id     TEXT PRIMARY KEY,    -- 8-char UUID prefix
    created_at TEXT,                -- ISO datetime
    mode       TEXT,                -- standing_no_brace, standing_with_brace, etc.
    result_json TEXT                -- Full analysis result as JSON blob
);
```

**`compliance.db`** — Brace wear-time and pressure data

```sql
CREATE TABLE wear_sessions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id           TEXT,
    started_at           TEXT,     -- ISO datetime
    ended_at             TEXT,     -- ISO datetime
    total_minutes        INTEGER,
    temperature_readings TEXT,     -- JSON blob
    status               TEXT DEFAULT 'active'
);

CREATE TABLE pressure_log (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id       TEXT,
    timestamp        TEXT,         -- ISO datetime
    upper_support    REAL,         -- kPa
    middle_pressure  REAL,         -- kPa
    lower_support    REAL,         -- kPa
    skin_temp        REAL,         -- Celsius
    brace_detected   INTEGER       -- 0/1
);
```

### Installation (Development)

```bash
# Clone
git clone https://github.com/yourusername/scoliosis-brace-coach.git
cd scoliosis-brace-coach

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

### Key Configuration Constants

| Constant | Value | Location | Purpose |
|---|---|---|---|
| `MAX_CONTENT_LENGTH` | 500 MB | `app.py` | Max upload file size |
| `MODEL_URL` | Google Storage URL | `pose_detector.py` | MediaPipe model download |
| `num_poses` | 1 | `pose_detector.py` | Detect single person |
| `min_detection_confidence` | 0.5 | `pose_detector.py` | Minimum pose confidence |
| Brace white threshold | > 20% | `brace_detector.py` | Torso pixel threshold for brace detection |
| Frame sample count | 10 | `video_processor.py` | Frames extracted from video |
| Progression critical | 5.0° (trunk) | `trend_analysis.py` | Alert threshold |
| Progression warning | 3.0° (trunk) | `trend_analysis.py` | Alert threshold |
| Prescribed hours | 23 hrs/day | `brace_pressure.py` | Compliance target |
| Pressure ranges | 40-60 / 50-70 / 35-55 kPa | `brace_pressure.py` | Correction point ideals |
| Skin temp baseline | 33.0°C | `brace_pressure.py` | Brace-worn detection threshold |

### Running Tests

The application includes an end-to-end test script:

```bash
python test_e2e.py
```

This tests all page routes, API endpoints, pressure evaluation, compliance tracking, and PDF generation.

### Extending the Application

**Add a new posture metric:**

1. Open `analysis/posture_rules.py`
2. Add your metric calculation using `detector.get_landmark_coords()` for landmark access
3. Add the metric to the return dictionary
4. Add a threshold in `AGE_THRESHOLDS`

**Add a new analysis mode:**

1. Open `analysis/video_processor.py`
2. Add a new `elif` branch in `process_media()`
3. Create a new rules file in `analysis/`
4. Add the mode option to `templates/index.html`

**Add a new API endpoint:**

1. Open `app.py`
2. Add a new `@app.route()` function
3. Follow the existing pattern for JSON responses

---

## API Reference

### Page Routes (HTML)

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page with upload form |
| `/results/<job_id>` | GET | Analysis results display |
| `/sensors` | GET | BLE sensor pairing and pressure monitoring |
| `/history` | GET | Session history table |
| `/compare` | GET | Side-by-side session comparison |
| `/dashboard` | GET | Clinician dashboard with KPIs |
| `/trends` | GET | Longitudinal trend charts |
| `/about` | GET | AIS treatment education |

### API Routes (JSON)

| Route | Method | Body/Params | Response |
|---|---|---|---|
| `/upload` | POST | `media` (file), `mode`, `age_group` | `{job_id}` |
| `/status/<job_id>` | GET | — | `{status, result}` |
| `/api/session/<job_id>` | GET | — | Full session JSON |
| `/api/trends` | GET | `?mode=` (optional) | Trend analysis |
| `/api/progression-report` | GET | — | Full progression report |
| `/api/pdf-report` | GET | — | PDF binary download |
| `/api/pressure/evaluate` | POST | `{upper_support, middle_pressure, lower_support, skin_temp}` | Pressure evaluation |
| `/api/compliance/start` | POST | `{session_id}` | Session started |
| `/api/compliance/log` | POST | `{session_id, upper_support, middle_pressure, lower_support, skin_temp, brace_detected}` | Reading logged |
| `/api/compliance/end` | POST | `{session_id}` | Compliance summary |
| `/api/compliance/summary/<id>` | GET | — | Compliance summary |
| `/api/pressure/history/<id>` | GET | — | Array of pressure readings |

### Example: Upload and Analyze

```bash
# Upload a photo
curl -X POST http://localhost:5000/upload \
  -F "media=@photo.jpg" \
  -F "mode=standing_no_brace" \
  -F "age_group=under15"

# Response: {"job_id": "a1b2c3d4"}

# Check status
curl http://localhost:5000/status/a1b2c3d4

# Response when done:
# {"status": "done", "result": {"status": "success", "mode": "standing_no_brace", ...}}
```

### Example: Evaluate Brace Pressure

```bash
curl -X POST http://localhost:5000/api/pressure/evaluate \
  -H "Content-Type: application/json" \
  -d '{"upper_support": 52, "middle_pressure": 63, "lower_support": 45, "skin_temp": 34.8}'

# Response:
# {
#   "status": "analyzed",
#   "score": 100.0,
#   "points": {
#     "upper_support": {"value": 52, "status": "optimal", "score": 100, ...},
#     "middle_pressure": {"value": 63, "status": "optimal", "score": 100, ...},
#     "lower_support": {"value": 45, "status": "optimal", "score": 100, ...}
#   },
#   "summary": "All correction points are at optimal pressure."
# }
```

### Example: Compliance Tracking

```bash
# Start monitoring
curl -X POST http://localhost:5000/api/compliance/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "patient_001"}'

# Log a pressure reading
curl -X POST http://localhost:5000/api/compliance/log \
  -H "Content-Type: application/json" \
  -d '{"session_id": "patient_001", "upper_support": 50, "middle_pressure": 60, "lower_support": 40, "skin_temp": 34.5, "brace_detected": true}'

# End session and get compliance summary
curl -X POST http://localhost:5000/api/compliance/end \
  -H "Content-Type: application/json" \
  -d '{"session_id": "patient_001"}'

# Response:
# {"total_wear_minutes": 480, "total_wear_hours": 8.0, "compliance_percentage": 5.8, "status": "poor"}
```

---

## Clinical Background

### What is Adolescent Idiopathic Scoliosis?

AIS is an abnormal lateral curvature of the spine that develops in adolescents (ages 10-18) with no known cause. It affects 2-3% of adolescents and is the most common spinal deformity in children.

### Treatment Hierarchy

```
Detection (Cobb angle measured via X-ray)
    │
    ├── Mild curves (< 25°) → Observation + Schroth exercises
    │
    ├── Moderate curves (25°-40°) → Bracing + Schroth exercises
    │   └── Goal: Prevent progression to surgical threshold
    │
    └── Severe curves (> 40-50°) → Spinal fusion surgery
        └── This tool aims to keep patients in the bracing category
```

### Why Bracing Works

The brace applies corrective forces at specific points on the torso to prevent the curve from worsening during growth. The BrAIST trial proved:

| Brace Wear Time | Surgery Avoidance Rate |
|---|---|
| < 6 hours/day | 41% |
| 6-12 hours/day | 60% |
| 13+ hours/day | 90% |
| 18+ hours/day | 90-95% |

### Why Schroth Exercises Help

The Schroth method is a scoliosis-specific exercise approach that:
- **Rotational Angular Breathing (RAB)** — Targets rotated ribs to derotate the spine
- **Muscle Cylinder Expansion** — Activates weak concave-side muscles
- **Postural Retraining** — Corrects habitual movement patterns

The 2025 SOSORT guidelines recommend Schroth PSSE over traditional physiotherapy for all curve patterns.

### How This Tool Fits In

```
Patient at home                    Clinic (every 4-6 months)
─────────────                      ──────────────────────────
Upload weekly photos               X-ray + Cobb angle measurement
     │                                    │
     ▼                                    ▼
See brace correction %              Review PDF reports
Track trends over weeks             Compare with previous visits
Get progression alerts              Make treatment decisions
     │                                    │
     ▼                                    ▼
Adjust brace/PT early  ◄────────  Adjust treatment plan
     │
     ▼
Avoid crossing surgical threshold
```

---

## Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-feature`
3. **Commit** your changes: `git commit -m "Add my feature"`
4. **Push** to the branch: `git push origin feature/my-feature`
5. **Open** a Pull Request

### Ideas for Contributions

- **Schroth Exercise Validation** — Pose classification for specific exercises
- **Real-Time Camera Overlay** — WebRTC-based positioning guide
- **Lighting Normalization** — Image preprocessing for consistent results
- **Cobb Angle Estimation** — ML model trained on paired surface/X-ray data
- **Multi-Language Support** — Internationalization for global use
- **Mobile App** — React Native or Flutter wrapper
- **Dark Mode** — UI theme toggle
- **Unit Tests** — Pytest test suite for all analysis modules

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Disclaimer

<div align="center">

### Medical Disclaimer

**This application is for educational and monitoring purposes only.**

This application is designed to assist parents and caregivers in tracking scoliosis
treatment progress between clinical visits. It is **not** intended to be used as a
substitute for professional medical advice, diagnosis, or treatment.

- This application is **not** a medical device and has **not** been reviewed or approved
  by the FDA or any medical regulatory body.
- The metrics displayed are **estimates** based on computer vision analysis of 2D images
  and should **not** be used as a basis for medical decisions.
- **Always** consult a qualified healthcare provider (physician, orthopedic specialist,
  or physical therapist) for clinical decisions regarding scoliosis treatment.
- **Never** ignore professional medical advice or delay seeking it because of information
  obtained from this application.

### Limitation of Liability

The author, **Srinath Sankara**, and contributors to this project assume **no responsibility
or liability** for any direct, indirect, incidental, special, exemplary, or consequential
damages arising from:

- Use or misuse of this application
- Any medical decisions made based on the output of this application
- Any errors or omissions in the content of this application
- Any interruptions or errors in the operation of this application

By using this application, you acknowledge that you have read this disclaimer, understand
its contents, and agree to use this application solely at your own risk.

### No Doctor-Patient Relationship

Use of this application does not create a doctor-patient, therapist-patient, or any
other professional healthcare relationship between the user and the application author.

</div>

---

<div align="center">

**Created by [Srinath Sankara](https://github.com/srinathsankara)**

Built with care for the scoliosis community.

If this tool helps your family, please consider sharing it with other families
affected by scoliosis.

</div>
