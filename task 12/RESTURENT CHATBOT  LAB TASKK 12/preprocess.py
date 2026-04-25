import os
import csv
import json
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    print('sentence-transformers not installed. Run `pip install -r requirements.txt`')
    raise

try:
    import faiss
except Exception:
    print('faiss not installed. Run `pip install -r requirements.txt`')
    raise

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, 'data', 'qna.csv')
FAISS_INDEX_PATH = os.path.join(BASE_DIR, 'faiss_index.index')
FAISS_META_PATH = os.path.join(BASE_DIR, 'faiss_meta.json')

MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'


def read_qna(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            q = r.get('question') or ''
            a = r.get('answer') or ''
            if q.strip():
                rows.append({'question': q.strip(), 'answer': a.strip()})
    return rows


def build_index(items, model_name=MODEL_NAME, index_path=FAISS_INDEX_PATH, meta_path=FAISS_META_PATH):
    model = SentenceTransformer(model_name)
    questions = [it['question'] for it in items]
    print('Computing embeddings for', len(questions), 'questions...')
    embeddings = model.encode(questions, convert_to_numpy=True, show_progress_bar=True)
    embeddings = embeddings.astype('float32')
    # normalize to use IndexFlatIP for cosine similarity
    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print('Saved FAISS index to', index_path)
    print('Saved metadata to', meta_path)


if __name__ == '__main__':
    if not os.path.exists(DATA_PATH):
        print('Data file not found at', DATA_PATH)
        print('Create a CSV at data/qna.csv with columns: question,answer')
        raise SystemExit(1)
    items = read_qna(DATA_PATH)
    if not items:
        print('No questions found in the dataset')
        raise SystemExit(1)
    build_index(items)
