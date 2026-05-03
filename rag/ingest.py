from pathlib import Path


def load_documents(folder_path: str):
    documents = []

    folder = Path(folder_path)

    for file_path in folder.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "filename": file_path.name,
            "content": content
        })

    return documents
