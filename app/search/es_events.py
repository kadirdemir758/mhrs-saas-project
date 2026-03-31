"""
MHRS SaaS — Elasticsearch SQLAlchemy Event Listeners
Automatically syncs Doctor records to ES after DB inserts/updates.

Register in app startup by calling: register_es_events()
"""
from sqlalchemy import event
from app.models.doctor import Doctor
from app.search.es_sync import index_doctor, delete_doctor


def _after_insert_doctor(mapper, connection, target: Doctor):
    """Triggered after a new Doctor row is inserted into MariaDB."""
    try:
        # Lazy-load clinic relationship via the instance state session
        from sqlalchemy.orm import Session
        session = Session.object_session(target)
        if session:
            session.refresh(target)
        index_doctor(target)
        print(f"✅ ES: Indexed new doctor_id={target.id} ({target.name})")
    except Exception as e:
        print(f"⚠️  ES after_insert_doctor failed for doctor_id={target.id}: {e}")


def _after_update_doctor(mapper, connection, target: Doctor):
    """Triggered after a Doctor row is updated in MariaDB."""
    try:
        from sqlalchemy.orm import Session
        session = Session.object_session(target)
        if session:
            session.refresh(target)

        if not target.is_active:
            # Soft-deleted doctor → remove from ES
            delete_doctor(target.id)
            print(f"🗑️  ES: Removed inactive doctor_id={target.id}")
        else:
            index_doctor(target)
            print(f"✅ ES: Re-indexed updated doctor_id={target.id} ({target.name})")
    except Exception as e:
        print(f"⚠️  ES after_update_doctor failed for doctor_id={target.id}: {e}")


def register_es_events() -> None:
    """
    Registers SQLAlchemy ORM event listeners for Doctor model.
    Call this once during application startup (e.g., in lifespan).
    """
    event.listen(Doctor, "after_insert", _after_insert_doctor)
    event.listen(Doctor, "after_update", _after_update_doctor)
    print("✅ Elasticsearch ORM event listeners registered for Doctor model.")
