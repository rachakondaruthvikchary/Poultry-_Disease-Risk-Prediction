# 🐔 PoultryGuardAI — Smart Poultry Disease Detection & Risk Prediction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

**An AI-powered system that learns normal poultry farm patterns, checks daily data for unusual changes, and provides early warning of possible disease risk — helping farmers prevent outbreaks before they become serious.**

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Docs](#-api-documentation) · [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Disease Coverage](#-disease-coverage)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Team](#-team)
- [License](#-license)

---

## 🎯 About the Project

**PoultryGuardAI** is an intelligent disease detection and risk prediction system designed for poultry farms. The model learns normal poultry farm patterns and checks daily data for unusual changes. If the changes are suspicious, it gives an **early warning** of possible disease risk.

This helps farmers notice potential health problems **before they become serious**. Instead of waiting for visible symptoms or large bird losses, the system **alerts the farmers** proactively.

### 🔑 Key Highlights

- 🧠 **CNN-based Image Classification** — Trained on 5,485+ poultry images to detect diseases from fecal samples
- 📊 **Risk Prediction Engine** — Uses Isolation Forest algorithm to detect anomalous farm patterns
- 🔔 **Early Warning System** — Alerts farmers before outbreaks escalate
- 📱 **Modern Web Dashboard** — Real-time monitoring with interactive charts and analytics
- 🔐 **Secure Authentication** — JWT-based user authentication system

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔬 **Disease Detection** | Upload poultry images for AI-powered disease classification |
| 📈 **Risk Assessment** | Analyze farm data to predict disease outbreak probability |
| 🗂️ **Disease Database** | Comprehensive information on 12 poultry diseases |
| 📊 **Analytics Dashboard** | Visual charts and trends for farm health monitoring |
| 🔔 **Alert System** | Automated notifications for high-risk situations |
| 👤 **User Management** | Secure login, registration, and profile management |
| 📋 **History Tracking** | Complete log of all predictions and assessments |
| 🌐 **REST API** | Well-documented API for integration with other systems |

---

## 🏗 Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│    Backend      │────▶│    AI Engine    │
│   (Next.js)     │     │   (FastAPI)     │     │  (TensorFlow)   │
│   Port: 3000    │     │   Port: 8000    │     │                 │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │                 │
                        │    Database     │
                        │   (SQLite)      │
                        │                 │
                        └─────────────────┘
```

---

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** JWT (JSON Web Tokens)
- **Server:** Uvicorn ASGI

### Frontend
- **Framework:** Next.js 14 (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Charts:** Recharts

### AI / Machine Learning
- **Deep Learning:** TensorFlow / Keras
- **Model:** Custom CNN (Convolutional Neural Network)
- **Anomaly Detection:** Isolation Forest (scikit-learn)
- **Image Processing:** Pillow, OpenCV

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- Git

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/rachakondaruthvikchary/Poultry-_Disease-Risk-Prediction.git
cd Poultry-_Disease-Risk-Prediction
```

**2. Set up the Backend**
```bash
cd Backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
python init_db.py
```

**3. Set up the Frontend**
```bash
cd Frontend
npm install
```

**4. Configure Environment**

Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./poultryguard.db
AI_MODEL_PATH=../AI/models/poultry_cnn.keras
```

### Running the Application

**Option 1: Quick Start (Windows)**
```bash
COMPLETE_STARTUP.bat
```

**Option 2: Manual Start**

Terminal 1 — Backend:
```bash
cd Backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Terminal 2 — Frontend:
```bash
cd Frontend
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| 🌐 Frontend | [http://localhost:3000](http://localhost:3000) |
| 📚 API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ❤️ Health Check | [http://localhost:8000/api/health](http://localhost:8000/api/health) |

### Default Credentials
```
Email:    test@test.com
Password: test1234
```

---

## 📂 Project Structure

```
PoultryGuardAI/
│
├── 🤖 AI/                          # AI & Machine Learning
│   ├── models/                     # Trained model files
│   │   ├── poultry_cnn.keras       # CNN classification model
│   │   ├── isolation_forest.pkl    # Risk prediction model
│   │   └── poultry_cnn_labels.json # Label mappings
│   ├── data/                       # Training datasets
│   ├── train_cnn.py                # CNN training script
│   ├── train_risk_model.py         # Risk model training
│   └── manage_datasets.py          # Dataset management tool
│
├── ⚙️ Backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # Application entry point
│   │   ├── models.py               # Database models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── auth.py                 # Authentication logic
│   │   └── routers/                # API route handlers
│   ├── disease_references/         # Reference data for diseases
│   ├── init_db.py                  # Database initialization
│   └── import_dataset.py           # Image import utility
│
├── 🎨 Frontend/                     # Next.js Frontend
│   ├── src/
│   │   ├── app/                    # App routes & pages
│   │   ├── components/             # React components
│   │   └── lib/                    # Utilities & API client
│   ├── public/                     # Static assets
│   └── package.json
│
├── 🗄️ Database/                     # Database schemas & migrations
│
├── 📜 scripts/                      # Utility scripts
│
├── disease_config.json             # Master disease configuration
├── COMPLETE_STARTUP.bat            # One-click startup (Windows)
├── START_BACKEND.bat               # Backend launcher
├── START_FRONTEND.bat              # Frontend launcher
├── verify_setup.py                 # System verification tool
└── README.md                       # You are here!
```

---

## 🦠 Disease Coverage

PoultryGuardAI is configured to detect **12 poultry diseases** across multiple categories:

### Currently Trainable (with image datasets)

| Disease | Images | Priority | Key Symptoms |
|---------|--------|----------|-------------|
| 🟢 Coccidiosis | 2,103 | HIGH | Bloody diarrhea, ruffled feathers, poor growth |
| 🟢 Healthy (Control) | 2,057 | CRITICAL | Normal baseline reference |
| 🟢 Salmonellosis-Pullorum | 949 | HIGH | Diarrhea, listlessness, dehydration |
| 🟢 Newcastle Disease | 376 | HIGH | Neurological signs, greenish diarrhea, twisted neck |

### Reference Data Available (expanding)

| Disease | Priority | Description |
|---------|----------|-------------|
| 🔴 Avian Influenza (Bird Flu) | CRITICAL | Highly contagious viral infection |
| 🟡 Infectious Bursal Disease | HIGH | Immunosuppressive viral disease |
| 🟡 Marek's Disease | HIGH | Viral neoplastic disease |
| 🟡 Infectious Bronchitis | HIGH | Viral respiratory disease |
| 🟡 Fowl Cholera | HIGH | Bacterial acute septicemia |
| 🟠 Fowl Pox | MEDIUM | Viral skin disease |
| 🟠 Mycoplasmosis (CRD) | MEDIUM | Chronic respiratory disease |
| 🟠 Infectious Coryza | MEDIUM | Bacterial upper respiratory infection |

> **Total Training Images:** 5,485 | **Total Diseases Configured:** 12

---

## 📡 API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login & get JWT token |
| `GET` | `/api/auth/me` | Get current user profile |

### Disease Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/predict/image` | Upload image for disease classification |
| `POST` | `/api/predict/risk` | Submit farm data for risk assessment |
| `GET` | `/api/predict/history` | Get prediction history |

### Disease Information
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/diseases` | List all diseases |
| `GET` | `/api/diseases/{id}` | Get disease details |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |

> 📖 Full interactive API documentation available at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

---

## 🧰 Available Tools & Scripts

```bash
# 🔍 System Health Check
python verify_setup.py

# 📊 Audit & Count Datasets
python AI/manage_datasets.py

# 📥 Import New Training Images
python Backend/import_dataset.py --disease "Disease Name" --source "path/to/images"

# 🚀 Start Everything (Windows)
COMPLETE_STARTUP.bat
```

---

## 👥 Team

**Developed by:** rachakondaruthvikchary

---

## 📄 License

This project is for educational and research purposes.

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for poultry farmers everywhere

</div>
