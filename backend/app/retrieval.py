from app.vector_store import get_index

_index = None
_query_engine = None


def get_query_engine():
    """Returns a cached query engine, building the index only once at startup."""
    global _index, _query_engine
    if _query_engine is None:
        _index = get_index()
        _query_engine = _index.as_query_engine(similarity_top_k=5)
    return _query_engine


def reindex():
    """Forces a rebuild of the index from whatever files currently exist in data/,
    and clears the cached query engine so the next call rebuilds it."""
    global _index, _query_engine
    _index = get_index(force_rebuild=True)
    _query_engine = _index.as_query_engine(similarity_top_k=5)
    return _query_engine