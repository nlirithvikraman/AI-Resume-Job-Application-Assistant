"""AI Resume & Job Application Assistant - Streamlit app.  Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from src import llm, tracker
from src.matcher import match, score_resume
from src.parser import extract_text, parse_resume

st.set_page_config(page_title="AI Resume Assistant", page_icon="📄", layout="wide")
st.title("📄 AI Resume & Job Application Assistant")

# ---------- sidebar: inputs ----------
with st.sidebar:
    st.header("1. Your inputs")
    api_key = st.text_input("Claude API key (optional if set in .env)", type="password")
    up = st.file_uploader("Resume (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"])
    jd = st.text_area("Paste job description", height=220)
    company = st.text_input("Company")
    role = st.text_input("Role")

resume_text = ""
if up:
    resume_text = extract_text(up.getvalue(), up.name)
    st.session_state["parsed"] = parse_resume(resume_text)
parsed = st.session_state.get("parsed")

if not parsed:
    st.info("Upload your resume in the sidebar to begin. Try `sample/resume.txt` and `sample/job.txt`.")
    st.stop()

kw = {"api_key": api_key or None}


def run_llm(fn, *args, **extra):
    try:
        with st.spinner("Asking Claude..."):
            return fn(*args, **extra, **kw)
    except llm.LLMError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"LLM call failed: {e}")


result = match(parsed.raw_text, jd) if jd.strip() else None
tabs = st.tabs(["Parsed resume", "Score", "Job match", "Tailor", "Cover letter",
                "Mock interview", "Roadmap", "Tracker"])

with tabs[0]:
    c1, c2 = st.columns(2)
    c1.subheader(parsed.name or "Name not detected")
    c1.write(f"📧 {parsed.email or '-'}  \n📞 {parsed.phone or '-'}")
    c1.write("🔗 " + (", ".join(parsed.links) or "-"))
    c2.write("**Detected skills**")
    c2.write(", ".join(parsed.skills) or "None detected")
    for sec, body in parsed.sections.items():
        with st.expander(sec.title()):
            st.text(body)
    st.download_button("Download parsed JSON", pd.Series(parsed.to_dict()).to_json(), "resume.json")

with tabs[1]:
    s, tips = score_resume(parsed)
    st.metric("Resume score", f"{s}/100")
    st.progress(s / 100)
    for t in tips:
        st.warning(t)
    if not tips:
        st.success("Looks solid!")

with tabs[2]:
    if not result:
        st.info("Paste a job description in the sidebar.")
    else:
        a, b, c = st.columns(3)
        a.metric("Match score", f"{result.score}%")
        b.metric("Skill coverage", f"{result.skill_coverage:.0%}")
        c.metric(f"Similarity ({result.method})", f"{result.similarity:.2f}")
        st.success("✅ Matched: " + (", ".join(result.matched_skills) or "none"))
        st.error("❌ Missing skills: " + (", ".join(result.missing_skills) or "none"))
        st.write("**Keywords from the job post not in your resume:** " + ", ".join(result.missing_keywords))

with tabs[3]:
    if st.button("Tailor my resume") and result:
        st.session_state["tailored"] = run_llm(llm.tailor_resume, parsed.raw_text, jd, result.missing_skills)
    if st.session_state.get("tailored"):
        st.markdown(st.session_state["tailored"])
        st.download_button("Download", st.session_state["tailored"], "tailored_resume.md")
        st.caption("Review every line. Only keep claims that are true for you.")

with tabs[4]:
    if st.button("Write cover letter") and jd:
        st.session_state["cover"] = run_llm(llm.cover_letter, parsed.raw_text, jd, name=parsed.name)
    if st.session_state.get("cover"):
        st.text_area("Cover letter", st.session_state["cover"], height=400)
        st.download_button("Download", st.session_state["cover"], "cover_letter.txt")

with tabs[5]:
    if st.button("Generate interview questions") and jd:
        qs = run_llm(llm.interview_questions, parsed.raw_text, jd)
        st.session_state["qs"] = qs
    if st.session_state.get("qs"):
        st.markdown(st.session_state["qs"])
        q = st.text_input("Which question are you answering? (paste it)")
        ans = st.text_area("Your answer", height=150)
        if st.button("Evaluate my answer") and q and ans:
            fb = run_llm(llm.evaluate_answer, q, ans, jd)
            if fb:
                st.markdown(fb)

with tabs[6]:
    weeks = st.slider("Weeks", 2, 16, 8)
    if st.button("Build roadmap") and result:
        out = run_llm(llm.learning_roadmap, parsed.raw_text, jd, result.missing_skills or result.missing_keywords[:6], weeks=weeks)
        if out:
            st.markdown(out)

with tabs[7]:
    st.subheader("Application tracker")
    if st.button("➕ Save this application") and company and role:
        tracker.add(company, role, "Saved", result.score if result else 0)
        st.rerun()
    rows = tracker.list_all()
    if rows:
        df = pd.DataFrame(rows, columns=["id", "company", "role", "status", "match", "date", "notes"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        c1, c2, c3 = st.columns(3)
        app_id = c1.selectbox("Application id", df["id"])
        new = c2.selectbox("New status", tracker.STATUSES)
        if c3.button("Update"):
            tracker.update_status(app_id, new); st.rerun()
        st.bar_chart(df["status"].value_counts())
    else:
        st.write("No applications yet.")
