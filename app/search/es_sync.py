"""
MHRS SaaS — Elasticsearch Sync Helpers
Indexes and deletes doctor documents from Elasticsearch.
Called by admin endpoints or after doctor create/update in DB.
"""
from app.search.es_client import get_es_client
from app.models.doctor import Doctor
from app.config import get_settings

settings = get_settings()


def _doctor_to_doc(doctor: Doctor) -> dict:
    """Converts a Doctor ORM object to an ES document body."""
    clinic = doctor.clinic
    return {
        "doctor_id":      doctor.id,
        "name":           doctor.name,
        "title":          doctor.title or "",
        "specialization": doctor.specialization,
        "clinic_id":      doctor.clinic_id,
        "clinic_name":    clinic.name if clinic else "",
        "city":           clinic.city.lower() if clinic else "",
        "district":       clinic.district.lower() if clinic else "",
        "clinic_type":    clinic.clinic_type or "" if clinic else "",
        "rating":         doctor.rating,
        "total_ratings":  doctor.total_ratings,
        "is_active":      doctor.is_active,
        "working_hours":  doctor.working_hours or "",
    }


def index_doctor(doctor: Doctor) -> None:
    """
    Upserts a doctor document into Elasticsearch.
    Use after creating or updating a doctor in MariaDB.
    """
    try:
        es = get_es_client()
        es.index(
            index=settings.elasticsearch_index_doctors,
            id=str(doctor.id),
            document=_doctor_to_doc(doctor),
        )
    except Exception as e:
        print(f"⚠️  ES index_doctor failed for doctor_id={doctor.id}: {e}")


def delete_doctor(doctor_id: int) -> None:
    """
    Removes a doctor document from Elasticsearch.
    Use after soft-deleting a doctor in MariaDB.
    """
    try:
        es = get_es_client()
        es.delete(
            index=settings.elasticsearch_index_doctors,
            id=str(doctor_id),
            ignore=[404],
        )
    except Exception as e:
        print(f"⚠️  ES delete_doctor failed for doctor_id={doctor_id}: {e}")


def bulk_reindex_all_doctors(db) -> int:
    """
    Re-indexes all active doctors from MariaDB into Elasticsearch.
    Use for initial setup or re-indexing after schema changes.

    Returns:
        Number of documents indexed.
    """
    from elasticsearch.helpers import bulk

    es = get_es_client()
    doctors = db.query(Doctor).filter(Doctor.is_active == True).all()

    actions = [
        {
            "_index": settings.elasticsearch_index_doctors,
            "_id": str(d.id),
            "_source": _doctor_to_doc(d),
        }
        for d in doctors
    ]

    if actions:
        success_count, _ = bulk(es, actions)
        print(f"✅ Bulk re-indexed {success_count} doctors into Elasticsearch.")
        return success_count
    return 0
