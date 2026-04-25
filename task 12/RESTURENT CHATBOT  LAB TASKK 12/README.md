# Semantic QnA with FAISS

This project adds semantic search for QnA using Hugging Face MiniLM and FAISS.

Quick setup:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python preprocess.py    # builds faiss_index.index and faiss_meta.json
python app.py           # starts Flask app on http://localhost:5000
```

Use the web UI on `/` to search semantically or chat with the regex bot.
