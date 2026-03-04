# AI Interview Practice Tool

Full-stack Django platform for realistic campus placement practice with complete interview lifecycle:

- Stage 1: Aptitude Round
- Stage 2: Coding Round
- Stage 3: Technical Round (role + login-resume based)
- Stage 4: HR Round
- Final: Overall score + downloadable PDF report

---

## 🔗 Live Demo

- Vercel Live Link: **https://ai-interview-practice-tool.vercel.app**

---

## ✨ What This Project Includes

- End-to-end 4-stage interview workflow with session progress tracking
- 500+ aptitude bank with randomized selection
- 100+ coding bank with visible/hidden test case style evaluation
- Role-focused technical round with resume-aware question generation
- Browser mic/camera/transcript workflow for technical and HR practice
- Stage-wise scoring, weighted overall result, readiness summary
- PDF report generation and download
- Mobile-friendly UI + dark/light mode
- Deployment-ready configuration for Vercel (plus Render/Railway/Fly support files)

---

## 🧠 Technical Roles Supported

Includes multiple tracks such as:

- AI/ML Engineer
- Data Scientist / Data Analyst
- Frontend / Backend / Full Stack / MERN
- Java / Python / JavaScript / PHP / .NET / Angular
- DevOps / Cloud / Cybersecurity / QA Automation
- Android / iOS
- Generative AI and more

---

## 🏗️ Tech Stack

- Backend: Django 5.x
- Database: PostgreSQL (recommended for production), SQLite (local/dev)
- Auth: Custom user fields (college, enrollment number)
- Static files: WhiteNoise
- Resume parsing: pypdf
- PDF reporting: reportlab
- Server process (non-serverless): gunicorn
- Deployment target: Vercel serverless Python runtime

Dependencies are maintained in:

- `requirements.txt` (root, delegates to backend)
- `backend/requirements.txt`

---

## 📁 Verified Project Structure

```text
AI_INTERVIEW_PRACTICE_TOOL/
├── api/
│   └── index.py                    # Vercel entry point (loads Django WSGI app)
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── DEPLOYMENT.md
│   ├── accounts/
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── interview/
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── services/
│   │   │   ├── code_runner.py
│   │   │   ├── question_precompute.py
│   │   │   ├── report_pdf.py
│   │   │   ├── resume_ai.py
│   │   │   └── whisperflow_client.py
│   │   └── management/commands/
│   │       ├── seed_aptitude_questions.py
│   │       └── seed_coding_questions.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── accounts/
│   │   └── interview/
│   ├── static/
│   └── media/
├── requirements.txt                # points to backend/requirements.txt
├── vercel.json
└── README.md
```

---

## ⚙️ Local Setup (Windows)

### 1) Clone and open backend folder

```powershell
git clone <your-repo-url>
cd AI_INTERVIEW_PRACTICE_TOOL\backend
```

### 2) Create + activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Install dependencies

```powershell
pip install -r requirements.txt
```

### 4) Configure environment

Create `.env` in `backend/` (or set environment variables manually). You can start from `backend/.env.example`:

```env
SECRET_KEY=change-me-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME

# Optional integrations
JUDGE0_API_URL=
JUDGE0_API_KEY=
```

### 5) Run migrations

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 6) Seed question banks (recommended)

```powershell
python manage.py seed_aptitude_questions
python manage.py seed_coding_questions
```

### 7) Run development server

```powershell
python manage.py runserver
```

Open in browser: `http://127.0.0.1:8000`

### 8) Quick project validation

```powershell
python manage.py check
```

---

## 🧭 User Flow

1. Sign up / Login
2. Start a new interview session
3. Attempt stages in order:
   - Aptitude → Coding → Technical → HR
4. View final overall result page
5. Download PDF report

---

## 📊 Scoring & Reports

- Each stage stores score + feedback
- Coding stage uses test-case based validation and detailed output messages
- Technical stage supports role-focused generated questions using resume context captured at login
- HR stage evaluates structured answers and transcript-supported responses
- Final report includes:
  - Overall score
  - Grade and readiness
  - Stage-wise performance
  - Strength and improvement areas

---

## ☁️ Vercel Deployment

Project already contains:

- `vercel.json` for Python serverless build routing through `api/index.py`
- Dynamic host/origin support in Django settings for `.vercel.app`

Deploy from project root:

```powershell
vercel login
vercel
vercel --prod
```

Set these environment variables in Vercel:

- `SECRET_KEY`
- `DEBUG=False`
- `DATABASE_URL`
- `ALLOWED_HOSTS=.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://your-project.vercel.app`

Important:

- Serverless filesystem is ephemeral, so persistent file writes should be avoided
- PDF response path is already implemented in a Vercel-safe way

For full multi-platform deployment notes: `backend/DEPLOYMENT.md`

---

## ✅ Current Status

- 4 interview rounds implemented
- Session progression + reports implemented
- PDF report generation implemented
- Mobile-friendly responsive UI implemented
- Vercel deployment structure configured

---

## 👩‍💻 Maintainer

- Email: rashmikad1743@gmail.com
- LinkedIn: https://www.linkedin.com/in/rashmika-makwana-39b0a6254
- GitHub: https://github.com/rashmikad1743

---

## ⭐ Support

If this project helps in your placement prep, please star the repository.
