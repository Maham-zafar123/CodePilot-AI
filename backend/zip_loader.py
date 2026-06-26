import zipfile
from pathlib import Path
from backend.config import UPLOAD_DIR


def save_and_extract_zip(uploaded_file) -> Path:
    project_name = Path(uploaded_file.name).stem.replace(" ", "_")
    extract_dir = UPLOAD_DIR / project_name
    extract_dir.mkdir(parents=True, exist_ok=True)
    zip_path = UPLOAD_DIR / uploaded_file.name
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    return extract_dir
