# YouTube Knowledge Extractor — Automatic Content Modes

Automatically classifies video transcripts and generates category-specific structured notes for education, entertainment, technical tutorials, podcasts/interviews, news/current affairs, documentaries, or general videos.

## Windows setup
```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```
Keep your existing `.env` and API key. Ensure `GEMINI_MODEL` is a model available to your Google AI Studio key. Then run:
```powershell
python -m streamlit run main.py
```

## What's retained
- SQLite transcript cache and summary library.
- Up to three attempts for temporary Gemini 503/429/server errors.
- Retry AI Generation reuses cached transcript.
- Existing databases are migrated by adding a `category` column; older summaries default to `general`.

Classification is based on transcript text, not audio language. English subtitles for Korean/Chinese audio can be classified and summarized in English. Classification is an AI estimate; short/ambiguous transcripts may be classified as general.
