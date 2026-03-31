"""
MHRS SaaS — Elasticsearch Index Mapping
Defines the 'doctors' index schema optimized for full-text + filter search.
"""
from app.search.es_client import get_es_client
from app.config import get_settings

settings = get_settings()

DOCTOR_INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,       # 0 replicas for single-node dev
        "analysis": {
            "analyzer": {
                "turkish_standard": {  # Extend with Turkish analyzer in production
                    "type": "standard",
                    "stopwords": "_none_",
                }
            }
        },
    },
    "mappings": {
        "properties": {
            "doctor_id":       {"type": "integer"},
            "name":            {"type": "text", "analyzer": "turkish_standard", "boost": 2.0},
            "title":           {"type": "keyword"},
            "specialization":  {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "clinic_id":       {"type": "integer"},
            "clinic_name":     {"type": "text", "analyzer": "turkish_standard"},
            "city":            {"type": "keyword"},
            "district":        {"type": "keyword"},
            "clinic_type":     {"type": "keyword"},
            "rating":          {"type": "float"},
            "total_ratings":   {"type": "integer"},
            "is_active":       {"type": "boolean"},
            "working_hours":   {"type": "text", "index": False},
        }
    },
}


def create_doctor_index() -> None:
    """
    Creates the doctors index if it does not already exist.
    Called on app startup via lifespan.
    """
    es = get_es_client()
    index_name = settings.elasticsearch_index_doctors
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=DOCTOR_INDEX_MAPPING)
        print(f"✅ Elasticsearch index '{index_name}' created.")
    else:
        print(f"ℹ️  Elasticsearch index '{index_name}' already exists.")
