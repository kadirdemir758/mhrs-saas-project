# MHRS SaaS — Hospital Appointment System

<div align="center">

```
  ███╗   ███╗██╗  ██╗██████╗ ███████╗    ███████╗ █████╗  █████╗ ███████╗
  ████╗ ████║██║  ██║██╔══██╗██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝
  ██╔████╔██║███████║██████╔╝███████╗    ███████╗███████║███████║███████╗
  ██║╚██╔╝██║██╔══██║██╔══██╗╚════██║    ╚════██║██╔══██║██╔══██║╚════██║
  ██║ ╚═╝ ██║██║  ██║██║  ██║███████║    ███████║██║  ██║██║  ██║███████║
  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
```

**Production-ready SaaS Hospital Appointment System**  
*FastAPI · MariaDB · Elasticsearch · RabbitMQ · Jenkins CI/CD*

</div>

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Mobile / Web Client                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS REST API (JSON)
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Application                           │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ ┌────────────────┐  │
│  │  /auth   │ │ /doctors │ │/appointments│ │/symptom-analyzer│  │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘ └───────┬────────┘  │
│       │            │              │                 │            │
│  ┌────▼────────────▼──────────────▼─────────────────▼────────┐  │
│  │           Security Layer (JWT + Encryption)               │  │
│  └────┬────────────────────────────────────────────────────-─┘  │
└───────┼─────────────────────────────────────────────────────────┘
        │
   ┌────┴──────────────────────────────────────────────────┐
   │                   Data & Message Layer                 │
   │                                                        │
   │  ┌──────────────┐  ┌───────────────┐  ┌────────────┐  │
   │  │   MariaDB    │  │ Elasticsearch │  │  RabbitMQ  │  │
   │  │  (Primary DB)│  │ (Doctor Search│  │ (Async Email│  │
   │  │  Users,      │  │    Index)     │  │  Tasks)    │  │
   │  │  Doctors,    │  └───────────────┘  └─────┬──────┘  │
   │  │  Appointments│                            │         │
   │  └──────────────┘               ┌────────────▼──────┐ │
   │                                 │  email_worker.py  │ │
   │                                 │  (SMTP Consumer)  │ │
   │                                 └───────────────────┘ │
   └────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start — Windows (Local Development)

### Prerequisites
- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) (with WSL2 backend)
- Python 3.12+
- Git

### Step 1 — Clone & Configure

```powershell
# Clone the repository
git clone https://github.com/your-org/mhrs-saas.git
cd mhrs-saas

# Create .env from template
Copy-Item .env.example .env
```

Open `.env` and fill in your credentials:
```dotenv
# Required for email to work
SMTP_USER=your_gmail@gmail.com
SMTP_PASSWORD=your_16_char_app_password   # Google → Security → 2FA → App Passwords

# Generate secure keys
JWT_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
ENCRYPTION_KEY=<run: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

### Step 2 — Start Infrastructure Services

```powershell
docker-compose up -d
```

Wait for health checks (~30 seconds):
```powershell
docker-compose ps
# All services should show "healthy"
```

| Service | URL | Credentials |
|---------|-----|-------------|
| RabbitMQ Management | http://localhost:15672 | mhrs_rabbit / rabbitpass |
| Elasticsearch | http://localhost:9200 | (none in dev) |
| MariaDB | localhost:3306 | mhrs_user / mhrs_password |

### Step 3 — Install Python Dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 4 — Start the API Server

```powershell
# Development with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> API is ready at **http://localhost:8000**  
> Swagger UI: **http://localhost:8000/docs**  
> ReDoc: **http://localhost:8000/redoc**

### Step 5 — Start the Email Worker (separate terminal)

```powershell
# Activate venv first
.venv\Scripts\Activate.ps1
python workers/email_worker.py
```

---

## 🧪 Running Tests

Tests use **in-memory SQLite** — no Docker required.

```powershell
python -m pytest tests/ -v --tb=short
```

Expected output:
```
tests/test_auth.py::test_register_success              PASSED
tests/test_auth.py::test_login_success                 PASSED
tests/test_appointments.py::test_create_appointment    PASSED
tests/test_appointments.py::test_double_booking_rejected PASSED
tests/test_encryption.py::test_encrypt_decrypt_roundtrip PASSED
tests/test_symptom_analyzer.py::test_cardiology_keywords PASSED
... (25+ tests)
```

---

## 🌐 API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register patient (TC encrypted, sends email) |
| POST | `/api/v1/auth/verify-email` | — | Verify 6-digit code |
| POST | `/api/v1/auth/login` | — | Returns JWT token |
| GET | `/api/v1/auth/me` | Bearer | Current user profile |

### Doctors & Clinics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/doctors/search?q=&city=&specialization=` | — | Elasticsearch full-text search |
| GET | `/api/v1/doctors/{id}` | — | Doctor detail |
| GET | `/api/v1/doctors/clinics/list?city=&clinic_type=` | — | List clinics |

### Appointments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/appointments` | Bearer | Book appointment (encrypted notes) |
| GET | `/api/v1/appointments` | Bearer | List my appointments |
| GET | `/api/v1/appointments/{id}` | Bearer | Appointment detail |
| PATCH | `/api/v1/appointments/{id}/cancel` | Bearer | Cancel appointment |

### Symptom Analyzer

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/symptom-analyzer` | — | Text → clinic suggestion |

**Example request:**
```bash
curl -X POST http://localhost:8000/api/v1/symptom-analyzer \
  -H "Content-Type: application/json" \
  -d '{"text": "I have chest pain and shortness of breath"}'
```
**Response:**
```json
{
  "input_text": "I have chest pain and shortness of breath",
  "suggested_clinic_type": "cardiology",
  "suggested_clinic_id": 1,
  "suggested_clinic_name": "Istanbul Kalp Hastanesi",
  "confidence": "high",
  "matched_keywords": ["chest pain", "shortness of breath"]
}
```

---

## 🔐 Security Architecture

### Encryption Module (`security/encryption_utils.py`)

Patient data uses **two-layer encryption** before reaching MariaDB:

```
Plaintext → [Layer 1: Custom Char Substitution] → [Layer 2: Fernet AES-128] → Ciphertext
```

- **Layer 1**: Configurable character substitution map, shuffled deterministically  
  from `CHAR_SUBSTITUTION_SEED` (changeable per tenant for white-labeling).
- **Layer 2**: Fernet (AES-128-CBC + HMAC-SHA256) — industry standard authenticated encryption.

The `ENCRYPTION_KEY` and `CHAR_SUBSTITUTION_SEED` in `.env` are the only secrets needed. **Change both before production deployment.**

---

## 🖥️ Ubuntu VM Production Deployment

### Prerequisites on Ubuntu Server

```bash
# Install Docker & Docker Compose
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin curl
sudo usermod -aG docker ubuntu
```

### Deploy Steps (Bridged Network)

```bash
# 1. Find VM IP (on Ubuntu)
ip addr show | grep 'inet '

# 2. On Ubuntu — create deploy directory
sudo mkdir -p /opt/mhrs-saas
sudo chown ubuntu:ubuntu /opt/mhrs-saas

# 3. Copy files (from Windows dev machine)
scp .env docker-compose.yml ubuntu@<VM_IP>:/opt/mhrs-saas/

# 4. SSH into VM
ssh ubuntu@<VM_IP>
cd /opt/mhrs-saas

# 5. Edit .env with production values
nano .env   # Set real ENCRYPTION_KEY, JWT_SECRET_KEY, SMTP credentials

# 6. Start all services
docker-compose up -d

# 7. Run the app (or use systemd below)
docker run -d --name mhrs_app \
  --env-file .env \
  --network mhrs-saas_mhrs_network \
  -p 8000:8000 \
  mhrs-saas:latest
```

### Systemd Service for Email Worker

Create `/etc/systemd/system/mhrs-email-worker.service`:

```ini
[Unit]
Description=MHRS Email Worker (RabbitMQ Consumer)
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/mhrs-saas
ExecStart=/opt/mhrs-saas/.venv/bin/python workers/email_worker.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/mhrs-saas/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable mhrs-email-worker
sudo systemctl start mhrs-email-worker
sudo systemctl status mhrs-email-worker
```

---

## 🔧 Jenkins CI/CD Setup

### Required Jenkins Plugins
- **Pipeline**
- **SSH Agent**
- **Git**
- **JUnit**

### Jenkins Credentials to Configure
Go to **Jenkins → Manage Jenkins → Credentials → Add:**

| ID | Type | Value |
|----|------|-------|
| `MHRS_VM_HOST` | Secret text | Ubuntu VM IP (e.g., `192.168.1.100`) |
| `MHRS_VM_USER` | Secret text | `ubuntu` |
| `MHRS_SSH_KEY` | SSH Username with private key | Your SSH private key |

### Create Jenkins Pipeline
1. New Item → Pipeline
2. Pipeline → Definition: **Pipeline script from SCM**
3. SCM: Git → enter your repository URL
4. Script Path: `Jenkinsfile`

### Pipeline Stages
```
Checkout → Install Deps → Run Tests → Build Docker Image → SSH Deploy to VM
```
After deploy, Jenkins SSHes into the VM, loads the new Docker image and runs a `/health` check.

---

## 📁 Project Structure

```
mhrs-saas/
├── app/
│   ├── main.py                   # FastAPI factory + lifespan
│   ├── config.py                 # Pydantic settings
│   ├── database.py               # SQLAlchemy engine + session
│   ├── models/                   # ORM models (User, Doctor, Clinic, Appointment)
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── routers/                  # API endpoint routers
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── appointments.py
│   │   └── symptom_analyzer.py
│   ├── search/                   # Elasticsearch client, mapping, sync
│   ├── messaging/                # RabbitMQ producer
│   └── services/                 # SMTP email service
│
├── security/
│   ├── encryption_utils.py       # Two-layer encryption module
│   └── auth.py                   # JWT + bcrypt + RBAC
│
├── workers/
│   └── email_worker.py           # Standalone RabbitMQ consumer
│
├── tests/                        # PyTest test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_appointments.py
│   ├── test_encryption.py
│   └── test_symptom_analyzer.py
│
├── scripts/
│   └── init.sql                  # MariaDB seed data (10 clinics, 10 doctors)
│
├── docker-compose.yml            # MariaDB + RabbitMQ + Elasticsearch
├── Dockerfile                    # Multi-stage production image
├── Jenkinsfile                   # CI/CD pipeline
├── requirements.txt
└── .env.example
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing secret (32+ bytes) | `secrets.token_hex(32)` |
| `ENCRYPTION_KEY` | Fernet key for patient data | `Fernet.generate_key()` |
| `CHAR_SUBSTITUTION_SEED` | Custom cipher seed (per-tenant) | `mycompany_seed_v1` |
| `DATABASE_URL` | MariaDB connection string | `mysql+pymysql://...` |
| `RABBITMQ_URL` | RabbitMQ AMQP URL | `amqp://user:pass@localhost/vhost` |
| `ELASTICSEARCH_URL` | ES endpoint | `http://localhost:9200` |
| `SMTP_USER` | Gmail address | `noreply@hospital.com` |
| `SMTP_PASSWORD` | Gmail App Password (16 chars) | `abcd efgh ijkl mnop` |

---

## 💰 SaaS Monetization Hooks

| Feature | Status | Notes |
|---------|--------|-------|
| Per-tenant `CHAR_SUBSTITUTION_SEED` | ✅ Ready | Rotate cipher per customer |
| Multi-clinic isolation | ✅ Ready | Filter by `clinic_id` |
| Role-based access (`patient`, `doctor`, `admin`) | ✅ Ready | `require_role()` dependency |
| Appointment reminders (RabbitMQ) | ✅ Ready | Wire scheduler to producer |
| NLP upgrade path | ✅ Stubbed | Replace `SYMPTOM_MAP` with ML model |
| Docker multi-tenant deployment | ✅ Ready | One image, env-per-tenant |
