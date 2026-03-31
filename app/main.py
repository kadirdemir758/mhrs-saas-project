"""
MHRS SaaS — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import create_all_tables, check_db_connection, SessionLocal
from app.models.user import User
from app.routers import auth, doctors, appointments, symptom_analyzer, slots, admin, users
from app.routers import locations
from app.models import location
from app.search.es_mapping import create_doctor_index
from app.search.es_events import register_es_events
from security.auth import hash_password
from security.encryption_utils import encrypt_field

settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs startup logic before serving requests, teardown after."""
    print(" MHRS SaaS starting up...")
    # 1. Create database tables
    create_all_tables()
    print("✅ Database tables verified.")
    
    # 2. Seed Super Admin
    try:
        db = SessionLocal()
        admin_email = "admin@mhrs.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            new_admin = User(
                tc_no_encrypted=encrypt_field("11111111111"),
                name="Sistem Yöneticisi",
                email=admin_email,
                hashed_password=hash_password("admin123"),
                role="admin",
                is_verified=True,
            )
            db.add(new_admin)
            db.commit()
            print(" Super Admin seed successful (admin@mhrs.com / admin123).")
        else:
            print("ℹ  Super Admin already exists.")
    except Exception as e:
        print(f"  Failed to seed Super Admin: {e}")
    finally:
        db.close()
        
    # 3. Create Elasticsearch index
    try:
        create_doctor_index()
        print(" Elasticsearch index verified.")
    except Exception as e:
        print(f"  Elasticsearch not available: {e}")
    # 3. Register SQLAlchemy → ES event listeners
    try:
        register_es_events()
    except Exception as e:
        print(f"  ES event listener registration failed: {e}")
    yield
    print(" MHRS SaaS shutting down.")


# ── FastAPI App Factory ────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "Production-ready Hospital Appointment System REST API. "
            "Mobile-first design, JWT authentication, encrypted medical records."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    from fastapi.middleware.cors import CORSMiddleware

    origins = [
        "http://localhost:5173",  # React'in çalıştığı yer
        "http://127.0.0.1:5173",
    ]

    # ── CORS ──────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,        # Restrict to your domain in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── API Routers ───────────────────────────────
    app.include_router(auth.router,              prefix="/api/v1", tags=["Authentication"])
    app.include_router(users.router,             prefix="/api/v1")
    app.include_router(doctors.router,           prefix="/api/v1", tags=["Doctors & Clinics"])
    app.include_router(appointments.router,      prefix="/api/v1", tags=["Appointments"])
    app.include_router(symptom_analyzer.router,  prefix="/api/v1", tags=["Symptom Analyzer"])
    app.include_router(slots.router,             prefix="/api/v1")
    app.include_router(locations.router,         prefix="/api/v1")
    app.include_router(admin.router,             prefix="/api/v1/admin")

    # ── Health Check ──────────────────────────────
    @app.get("/health", tags=["System"])
    def health_check():
        db_ok = check_db_connection()
        return JSONResponse({
            "status": "healthy" if db_ok else "degraded",
            "service": settings.app_name,
            "database": "connected" if db_ok else "unreachable",
        })

    @app.get("/", tags=["System"])
    def root():
        return {"message": f"Welcome to {settings.app_name} API", "docs": "/docs"}

    return app


app = create_app()
