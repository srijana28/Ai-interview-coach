# AI Interview Coach

This is a RAG-based AI Interview Coach built with Python and LangChain. It generates mock interview questions, evaluates candidate answers, and produces a final performance report.

## What it does

- Uses retrieval-augmented generation (RAG) to create interview questions from a job description
- Supports question generation, answer evaluation, and interview report generation
- Stores conversation state in memory while running
- Includes both a CLI and a Streamlit web UI

## Key features

- Gemini / Google GenAI integration for LLM and embeddings
- Chroma vector store for semantic retrieval from job descriptions
- Structured feedback using pydantic models
- Adaptive interview flow with follow-up questions

## Setup

1. Create and activate your virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run

### Streamlit web app

```powershell
streamlit run app.py
```

### CLI app

```powershell
python main.py --job data/job_description/senior_python.txt --type technical --level senior --questions 5
```

## Project structure

- `app.py` — Streamlit interface
- `main.py` — CLI entrypoint
- `interview_coach.py` — interview orchestration
- `chains/` — LLM chains for asking questions and evaluating answers
- `rag/` — retrieval and question generation from job descriptions
- `models/` — feedback and report data models
- `config.py` — settings and environment loading

## Notes

- Keep `.env` out of source control; it contains sensitive API keys.
- Ensure `GEMINI_API_KEY` is set before running the app.
