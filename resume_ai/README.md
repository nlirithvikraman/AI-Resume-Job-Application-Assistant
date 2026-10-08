# AI Resume & Job Application Assistant

Full job-application assistant (Idea 8 from the project plan): parse a resume, score it, match it to a
job description (ATS-style), tailor bullets, write a cover letter, run a mock interview, build a skill-gap
roadmap, and track applications.

**Stack:** Python · Streamlit · pdfplumber · python-docx · scikit-learn (TF-IDF) · Sentence-Transformers (optional) · spaCy (optional) · Claude API · SQLite

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm                # optional
cp .env.example .env                                   # add your ANTHROPIC_API_KEY
streamlit run app.py
pytest                                                 # run tests
```
No API key? Parser, scorer, matcher and tracker still work; only the LLM tabs need a key.
Sentence-Transformers/spaCy are optional; the app falls back to TF-IDF and heuristics automatically.

## Structure
| File | Stage | Purpose |
|---|---|---|
| `src/parser.py` | 1 | PDF/DOCX/TXT text extraction, contact info, sections, skills |
| `src/matcher.py` | 2 | Match %, missing skills/keywords, resume score |
| `src/llm.py` | 3 | Tailoring, cover letter, interview, roadmap (Claude) |
| `src/tracker.py` | 4 | SQLite application dashboard |
| `app.py` | UI | Streamlit app with 8 tabs |
| `tests/` | | pytest suite |

## Build order (suggested weeks)
1. Week 1: parser + tests. 2. Week 2: matcher + scorer. 3. Week 3: LLM tabs. 4. Week 4: tracker, polish, deploy.

## Deploy (free)
Push to GitHub, then Streamlit Community Cloud or Hugging Face Spaces. Add `ANTHROPIC_API_KEY` as a secret.

## Next improvements
- Job recommendations: embed job postings in ChromaDB/FAISS and query with the resume embedding.
- Recruiter mode: rank many resumes against one JD.
- Export tailored resume to DOCX/PDF (python-docx / ReportLab).
- Expand `src/skills.py` or replace with a spaCy `EntityRuler`.

## Ethics note
The prompts forbid inventing experience. Always review AI output before sending it to an employer.
