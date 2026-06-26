import chromadb
from chromadb.utils import embedding_functions
from backend.config import VECTOR_DIR
from backend.chunker import build_chunks


def get_collection(project_name: str):
    client = chromadb.PersistentClient(path=str(VECTOR_DIR / project_name))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_or_create_collection(name="code_chunks", embedding_function=embedding_fn)


def index_project(project_name: str, files):
    collection = get_collection(project_name)
    docs = build_chunks(files)
    if not docs:
        return 0
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metas = [d["metadata"] for d in docs]
    collection.upsert(ids=ids, documents=texts, metadatas=metas)
    return len(docs)


def search_project(project_name: str, query: str, n_results: int = 6):
    collection = get_collection(project_name)
    result = collection.query(query_texts=[query], n_results=n_results)
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    return list(zip(docs, metas))
