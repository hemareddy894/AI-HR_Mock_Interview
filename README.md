# AI Mock HR Interview

An AI-powered voice interview platform for college placement preparation. Students select a job role, upload their resume, and receive a fully personalized HR interview with voice questions, speech-to-text answers, dynamic follow-up questions, and a detailed performance report.

---

## Features

- Resume-based personalized questions
- Voice interview (Text-to-Speech + Speech-to-Text)
- Dynamic follow-up questions based on previous answers
- STAR method analysis for behavioral questions
- Resume claim verification
- AI answer evaluation (relevance, clarity, structure, completeness)
- Final HR performance report with scores
- Personalized improvement plan
- Weak area practice
- Interview history with progress chart
- Demo Mode (works without AI API)
- Glassmorphism UI

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| Database | MySQL |
| AI | Google Gemini / OpenAI GPT |
| Resume Parsing | pdfplumber, python-docx |
| Voice (STT) | Browser Web Speech API |
| Voice (TTS) | Browser SpeechSynthesis API |
| Charts | Chart.js |

---

## Folder Structure

```
AI-HR-INTERVIEW/
├── app.py                  # Flask app factory + entry point
├── config.py               # Configuration from .env
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example            # Template for .env
├── routes/
│   ├── main_routes.py      # Page routes
│   └── api_routes.py       # API endpoints
├── services/
│   ├── ai_service.py       # AI functions (analyze, generate, evaluate)
│   ├── resume_service.py   # PDF/DOCX parsing
│   └── evaluation_service.py # Answer evaluation + report building
├── models/
│   └── __init__.py         # SQLAlchemy models
├── templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── select_role.html
│   ├── upload_resume.html
│   ├── analyzing.html
│   ├── interview_setup.html
│   ├── interview.html
│   ├── report.html
│   ├── history.html
│   └── practice.html
├── static/
│   └── css/style.css       # Glassmorphism styles
├── uploads/                # Uploaded resumes (auto-created)
└── database/
    └── schema.sql          # MySQL schema + seed data
```

---

## Installation

### 1. Clone / Download the project

```bash
cd "AI Mock HR Interview"
```

### 2. Create Python virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. MySQL Setup

Make sure MySQL is running, then:

```sql
-- Option A: Run the schema file
mysql -u root -p < database/schema.sql

-- Option B: Just create the database (Flask will create tables automatically)
CREATE DATABASE ai_hr_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure .env

Copy `.env.example` to `.env` and fill in your values:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env`:

```env
SECRET_KEY=your-random-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ai_hr_interview

# For real AI: set AI_PROVIDER and API key
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key

# For Demo Mode (no API needed):
AI_PROVIDER=demo
DEMO_MODE=true
```

### 6. Run the application

```bash
python app.py
```

Open: http://localhost:5000

---

## AI API Configuration

### Google Gemini (Recommended — Free Tier Available)

1. Go to https://aistudio.google.com/app/apikey
2. Create an API key
3. Set in `.env`:
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your-key-here
   DEMO_MODE=false
   ```

### OpenAI GPT

1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Set in `.env`:
   ```
   AI_PROVIDER=openai
   OPENAI_API_KEY=your-key-here
   DEMO_MODE=false
   ```

---

## Demo Mode

Set in `.env`:
```
AI_PROVIDER=demo
DEMO_MODE=true
```

Demo Mode simulates resume analysis, questions, evaluations, and reports without any API key. All pages are fully functional. A "Demo Mode" badge appears in the UI.

---

## Browser Microphone Permissions

- The interview uses the browser's Web Speech API
- When the microphone button is pressed, the browser will ask for permission
- Allow microphone access when prompted
- Works best in Chrome or Edge
- Firefox has limited Web Speech API support
- If speech recognition is unavailable, a text input fallback is shown

---

## Database Schema

Tables: `users`, `roles`, `resumes`, `candidate_profiles`, `interviews`, `questions`, `answers`, `evaluations`, `reports`

See `database/schema.sql` for full schema with foreign keys and indexes.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in venv |
| MySQL connection error | Check DB credentials in `.env`, ensure MySQL is running |
| Resume parse error | Ensure file is a valid PDF/DOCX, not password-protected |
| Microphone not working | Use Chrome/Edge, allow mic permission, use HTTPS in production |
| AI API error | Check API key in `.env`, or switch to `DEMO_MODE=true` |
| Tables not created | Flask auto-creates tables on startup; check DB credentials |

---

## Future Enhancements

- User authentication (login/register)
- Video recording of interview
- Emotion/confidence analysis
- Company-specific interview modes
- Export report as PDF
- Email report to candidate
- Admin dashboard
- Multi-language support
