"""Stage 3: LLM features via the Claude API."""
import os

from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

HONESTY = (
    "Never invent experience, employers, degrees, metrics or skills. "
    "Only use facts present in the resume. If something is missing, say so instead of making it up."
)


class LLMError(RuntimeError):
    pass


def _ask(system: str, user: str, api_key: str | None = None, max_tokens: int = 1500) -> str:
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise LLMError("No API key. Set ANTHROPIC_API_KEY in .env or paste it in the sidebar.")
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=f"{system}\n\n{HONESTY}",
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def tailor_resume(resume: str, jd: str, missing_skills: list, **kw) -> str:
    return _ask(
        "You are an expert resume coach.",
        f"Rewrite the resume's experience/project bullets to fit this job. Use strong verbs, keep facts unchanged, "
        f"work in these keywords ONLY where truthful: {', '.join(missing_skills) or 'none'}.\n"
        f"Output: a rewritten summary, then rewritten bullets grouped by role/project, then a short list of "
        f"'gaps you cannot honestly claim'.\n\nRESUME:\n{resume}\n\nJOB:\n{jd}", **kw)


def cover_letter(resume: str, jd: str, name: str = "", **kw) -> str:
    return _ask(
        "You write concise, specific cover letters (under 300 words, no clichés).",
        f"Write a tailored cover letter for {name or 'the candidate'}.\n\nRESUME:\n{resume}\n\nJOB:\n{jd}", **kw)


def interview_questions(resume: str, jd: str, n: int = 8, **kw) -> str:
    return _ask(
        "You are a hiring manager.",
        f"Generate {n} interview questions (mix technical, behavioural, resume-specific). Number them.\n\n"
        f"RESUME:\n{resume}\n\nJOB:\n{jd}", **kw)


def evaluate_answer(question: str, answer: str, jd: str, **kw) -> str:
    return _ask(
        "You are a supportive interview coach.",
        f"Question: {question}\nAnswer: {answer}\nJob context: {jd[:1500]}\n\n"
        f"Give: score /10, what was good, what was missing, and an improved sample answer structure (STAR if relevant).", **kw)


def learning_roadmap(resume: str, jd: str, missing_skills: list, weeks: int = 8, **kw) -> str:
    return _ask(
        "You are a career mentor.",
        f"Create a {weeks}-week learning roadmap to close these skill gaps: {', '.join(missing_skills)}. "
        f"For each week: topic, a free resource type, and one small portfolio project.\n\nRESUME:\n{resume}\n\nJOB:\n{jd}", **kw)
