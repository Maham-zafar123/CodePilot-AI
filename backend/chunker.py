def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = max(end - overlap, end)
    return chunks


def build_chunks(files):
    docs = []
    for file in files:
        for i, chunk in enumerate(chunk_text(file["content"])):
            docs.append({
                "id": f'{file["path"]}::chunk_{i}',
                "text": chunk,
                "metadata": {"path": file["path"], "extension": file["extension"], "chunk": i},
            })
    return docs
