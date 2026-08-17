# 📚 StudyGen

### AI-Powered Personal Study Assistant

**Learn • Understand • Practice • Remember**

StudyGen is a modular AI study platform that combines AI chat, study-material generation, quizzes, PDF learning, multi-provider AI routing, Firebase persistence, and learning progress into one unified study environment.

---

## 🌟 Overview

StudyGen is designed to help students learn from a single workspace instead of switching between multiple applications.

### Core Features

- 💬 AI Study Chat
- 📚 AI Study Material Generation
- 📝 Exam Answer Generation
- 🎯 AI Quiz Generation
- 🧠 Flashcards
- 📄 Large PDF Processing
- 🔥 Firebase Data Storage
- 🤖 Multiple AI Providers
- 🔄 Automatic AI Provider Failover
- 📊 Learning Progress
- 🗂️ Persistent Study History

The long-term goal is to transform StudyGen from a simple AI chatbot into a **personal AI learning companion**.

---

# 🎯 Vision

Most AI applications are designed around:

> Ask → Answer

StudyGen is being designed around:

> **Understand → Practice → Evaluate → Remember → Improve**

```text
                 ┌─────────────────┐
                 │     STUDENT     │
                 └────────┬────────┘
                          │
                          ▼
                ┌───────────────────┐
                │     UNDERSTAND    │
                │ AI Chat           │
                │ Explanations      │
                │ Study Materials   │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │      PRACTICE     │
                │ Quizzes           │
                │ MCQs              │
                │ Flashcards        │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │      EVALUATE     │
                │ Scores / Mistakes │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │      REMEMBER     │
                │ Firebase          │
                │ Chat / Study Data│
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │      IMPROVE      │
                │ Personalized      │
                │ Learning          │
                └───────────────────┘
```

---

# 🤖 Multi-Provider AI Architecture

StudyGen uses an AI Router instead of tightly coupling the application to one provider.

```text
                    ┌──────────────┐
                    │   StudyGen   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   AI Router  │
                    └──────┬───────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Gemini         OpenAI      OpenRouter
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                         Groq
```

Providers can be configured with:

```text
Provider Name
API Key
Model
Base URL
Priority
Enabled / Disabled
```

---

# 🔄 Automatic AI Failover

If a configured provider becomes unavailable because of quota exhaustion, timeout, outage, or another provider error, the router can attempt another provider.

```text
                     STUDYGEN
                         │
                         ▼
                    AI ROUTER
                         │
                         ▼
                    ┌─────────┐
                    │ Gemini  │
                    └────┬────┘
                         │
                    ❌ Failure
                         │
                         ▼
                    ┌─────────┐
                    │ OpenAI  │
                    └────┬────┘
                         │
                    ❌ Failure
                         │
                         ▼
                    ┌─────────┐
                    │  Groq   │
                    └────┬────┘
                         │
                    ❌ Failure
                         │
                         ▼
                  ┌─────────────┐
                  │ OpenRouter  │
                  └─────────────┘
```

---

# 📄 Large PDF Processing

StudyGen is designed to process large study PDFs using a document-processing pipeline.

```text
                    ┌───────────┐
                    │    PDF    │
                    └─────┬─────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ PDF Extraction  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Text Processing │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Smart Chunking  │
                 └────────┬────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
           Chunk 1      Chunk 2     Chunk 3
              │           │           │
              └───────────┼───────────┘
                          │
                          ▼
                    ┌───────────┐
                    │ AI Router │
                    └─────┬─────┘
                          │
                          ▼
                  Study Generation
```

### Processing Flow

```text
PDF
 ↓
Extract
 ↓
Clean
 ↓
Detect size
 ↓
Split into chunks
 ↓
Process chunks
 ↓
Combine results
 ↓
Generate final answer
```

For scanned PDFs, the planned OCR pipeline is:

```text
Scanned PDF
     │
     ▼
Page Images
     │
     ▼
OCR
     │
     ▼
Extracted Text
     │
     ▼
Chunking
     │
     ▼
AI Processing
```

---

# 🎯 AI Quiz System

```text
                 ┌──────────────┐
                 │ Choose Topic │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Generate Quiz│
                 └──────┬───────┘
                        │
                        ▼
                ┌────────────────┐
                │ Display MCQs   │
                └───────┬────────┘
                        │
                        ▼
                 Student Answers
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
          Correct              Wrong
             🟢                  🔴
              │                   │
              └─────────┬─────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Final Score  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Save Result  │
                 └──────────────┘
```

---

# 🔥 Firebase Architecture

Firebase is designed to act as the persistent data layer.

```text
                    STUDYGEN
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        ┌───────────┐       ┌────────────┐
        │ AI Router │       │  Firebase  │
        └─────┬─────┘       └──────┬─────┘
              │                    │
              ▼                    ▼
        AI Generation        Persistent Data
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
                  Chats         Quizzes        Progress
```

Planned Firestore structure:

```text
users
└── {uid}
    ├── chats
    │   └── messages
    ├── study_materials
    ├── quizzes
    ├── quiz_attempts
    ├── notes
    └── progress
```

Firebase stores student data while AI providers handle reasoning and generation.

---

# 🏗️ Complete System Architecture

```text
                         ┌────────────────────┐
                         │      STUDENT       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │     FRONTEND       │
                         │   HTML / CSS / JS  │
                         └─────────┬──────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
                  Chat           PDF            Quiz
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      FASTAPI       │
                         │      BACKEND       │
                         └─────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │  AI Router  │      │ PDF Engine  │      │ Quiz Engine │
       └──────┬──────┘      └─────────────┘      └─────────────┘
              │
      ┌───────┼────────┬──────────┐
      ▼       ▼        ▼          ▼
   Gemini   OpenAI    Groq    OpenRouter

                         ┌────────────────────┐
                         │      FIREBASE      │
                         │ Auth / Firestore   │
                         │ Storage            │
                         └────────────────────┘
```

---

# 🔁 Request Flow

```text
Student
  │
  ▼
Frontend
  │
  ▼
FastAPI
  │
  ├── Normal Chat ──────► AI Router
  │
  ├── Study Request ────► Study Generator
  │
  ├── PDF ───────────────► PDF Processor
  │
  └── Quiz ──────────────► Quiz Engine
                                │
                                ▼
                           AI Provider
                                │
                                ▼
                         Response Parser
                                │
                                ▼
                            Firebase
                                │
                                ▼
                            Frontend
```

---

# 🧩 Backend Structure

```text
backend/
├── main.py
├── ai_router.py
├── ai_service.py
├── config.py
├── provider_config.py
├── provider_manager.py
├── provider_registry.py
├── provider_store.py
│
├── providers/
│   ├── base.py
│   ├── gemini.py
│   ├── openai.py
│   ├── openai_compatible.py
│   └── openrouter.py
│
├── pdf_processor.py
├── quiz_engine.py
├── quiz_store.py
├── response_parser.py
├── study_generator.py
├── study_material.py
└── requirements.txt
```

| Module | Responsibility |
|---|---|
| `main.py` | FastAPI application and API routes |
| `ai_router.py` | AI provider selection and failover |
| `ai_service.py` | AI service abstraction |
| `provider_manager.py` | Provider lifecycle management |
| `provider_registry.py` | Provider registration |
| `provider_config.py` | Provider configuration |
| `provider_store.py` | Provider persistence |
| `providers/` | Individual AI provider implementations |
| `pdf_processor.py` | PDF extraction and processing |
| `quiz_engine.py` | Quiz generation and logic |
| `quiz_store.py` | Quiz persistence |
| `response_parser.py` | AI response parsing |
| `study_generator.py` | Study content generation |
| `study_material.py` | Study material processing |

---

# 🌐 Frontend Structure

```text
frontend/
├── index.html
├── app.js
└── style.css
```

- `index.html` — application interface
- `style.css` — layout, chat UI, quiz UI, cards, animations
- `app.js` — API communication, chat, quizzes, PDF upload, Firebase, provider management

---

# 🔌 API

### System

```text
GET /
```

### Providers

```text
GET    /providers
GET    /providers/config
POST   /providers
GET    /providers/{provider}
PATCH  /providers/{provider}/enable
PATCH  /providers/{provider}/disable
DELETE /providers/{provider}
POST   /providers/{provider}/test
```

### AI

```text
POST /generate
```

Example:

```json
{
  "prompt": "Explain Artificial Intelligence",
  "provider": "gemini"
}
```

### Study Generation

```text
POST /study/generate
```

Example:

```json
{
  "topic": "Artificial Intelligence",
  "content_type": "mcq",
  "difficulty": "medium",
  "count": 5
}
```

---

# 📖 API Documentation

When the backend is running:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides an interactive API testing interface.

---

# ⚙️ Installation

## Requirements

- Python 3.11+
- Git
- Modern web browser
- Internet connection

## Clone

```bash
git clone https://github.com/riyasharavind-dev/StudyGen.git
cd StudyGen
```

## Create Virtual Environment

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

If required:

```bash
pip install pypdf
```

---

# ▶️ Run Backend

```powershell
cd backend
python -m uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API Docs:

```text
http://127.0.0.1:8000/docs
```

---

# ▶️ Run Frontend

Open another terminal:

```powershell
cd frontend
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

Use a local HTTP server instead of opening `index.html` directly because the application uses JavaScript modules and Firebase.

---

# 🔐 Security

Never commit real credentials.

Do not commit:

```text
.env
providers.json
service-account.json
Firebase private keys
API keys
Secret tokens
Passwords
```

Use environment variables or local configuration.

Example:

```env
GEMINI_API_KEY=
OPENAI_API_KEY=
GROQ_API_KEY=
```

---

# 🧪 Testing

### Backend

```text
http://127.0.0.1:8000
```

### Swagger

```text
http://127.0.0.1:8000/docs
```

### Providers

```text
GET /providers
```

### Provider Test

```text
POST /providers/{provider_name}/test
```

### Study Generation

```text
POST /study/generate
```

### PDF

Upload a study PDF through the frontend and generate explanations, summaries, notes, quizzes, or flashcards.

---

# 🛠️ Development Workflow

```text
              ┌──────────────┐
              │  Idea / Bug  │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Implement    │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Run Backend  │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Test API     │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Test Frontend│
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Git Commit   │
              └──────┬───────┘
                     │
                     ▼
              ┌──────────────┐
              │ Git Push     │
              └──────────────┘
```

Typical Git workflow:

```bash
git status
git add .
git commit -m "Describe the change"
git push
```

---

# 🗺️ Roadmap

## ✅ Foundation

- [x] FastAPI backend
- [x] Modular backend architecture
- [x] AI provider abstraction
- [x] Gemini integration
- [x] OpenAI integration architecture
- [x] OpenRouter integration architecture
- [x] OpenAI-compatible provider architecture
- [x] Provider priority
- [x] Provider enable / disable
- [x] Provider testing
- [x] AI failover architecture
- [x] PDF extraction
- [x] Large-document processing architecture
- [x] Study generation
- [x] Quiz engine
- [x] Firebase foundation
- [x] Web frontend

## 🚧 In Development

- [ ] Natural StudyBot conversation mode
- [ ] Context-aware chat
- [ ] Persistent chat history
- [ ] Complete Firebase integration
- [ ] Firebase-powered study memory
- [ ] Scanned PDF OCR
- [ ] Advanced PDF intelligence
- [ ] Better quiz UI
- [ ] Detailed quiz analytics
- [ ] Personalized study recommendations

## 🔮 Future

- [ ] Voice StudyBot
- [ ] Mobile application
- [ ] Long-term learning memory
- [ ] Knowledge graph
- [ ] Adaptive quizzes
- [ ] AI study planning
- [ ] Revision reminders
- [ ] Personalized curriculum
- [ ] Offline study capabilities
- [ ] Personal AI tutor

---

# 🧠 Design Philosophy

### Modular

Major capabilities should be independently replaceable.

```text
AI
PDF
Quiz
Firebase
Frontend
```

### Provider Independent

The application should not permanently depend on a single AI provider.

```text
Gemini
OpenAI
Groq
OpenRouter
Custom Providers
```

can exist behind the AI Router.

### Data First

Learning history belongs to the student.

AI providers generate responses.

Firebase stores the student's information.

### Learning Oriented

The objective is not simply to generate text.

```text
Understand
   ↓
Practice
   ↓
Test
   ↓
Review
   ↓
Improve
```

---

# 🌍 Why StudyGen?

Students often use different applications for:

```text
AI Chat
PDF Reading
Notes
Flashcards
Quizzes
Progress Tracking
Study Planning
```

StudyGen aims to combine these capabilities into one intelligent environment.

```text
        AI CHAT
           +
        PDF STUDY
           +
          NOTES
           +
        QUIZZES
           +
       FLASHCARDS
           +
        PROGRESS
           +
      AI PROVIDERS
           +
        FIREBASE
           │
           ▼
       ┌─────────┐
       │ StudyGen│
       └─────────┘
```

---

# 👨‍💻 Developer

## Riyash Aravind

AI & Data Science Engineering Student

StudyGen is an exploration into:

- Artificial Intelligence
- AI application architecture
- Multi-provider AI systems
- AI routing
- Educational technology
- Document intelligence
- Firebase applications
- Adaptive learning
- Personal AI assistants

---

# ⭐ Support

If you find StudyGen interesting:

⭐ Star the repository  
🍴 Fork the project  
🐛 Report bugs  
💡 Suggest features  
🤝 Contribute improvements

GitHub:

https://github.com/riyasharavind-dev/StudyGen

---

# 📜 License

StudyGen is currently under active development.

License information will be added when the project reaches its stable public-release stage.

---

<p align="center">

# 📚 StudyGen

### Learn smarter. Practice better. Remember longer.

**An AI study assistant built for students.**

</p>
