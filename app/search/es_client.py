"""
MHRS SaaS — Elasticsearch Client Singleton
"""
from elasticsearch import Elasticsearch
from app.config import get_settings

settings = get_settings()
_es_client: Elasticsearch | None = None


def get_es_client() -> Elasticsearch:
    """
    Returns a singleton Elasticsearch client.
    Raises ConnectionError if ES is unreachable.
    """
    global _es_client
    if _es_client is None:
        _es_client = Elasticsearch(
            hosts=[settings.elasticsearch_url],
            request_timeout=10,
            retry_on_timeout=True,
            max_retries=3,
        )
    if not _es_client.ping():
        raise ConnectionError(f"Elasticsearch at {settings.elasticsearch_url} is unreachable.")
    return _es_client
