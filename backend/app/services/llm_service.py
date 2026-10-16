import json

from groq import Groq

from app.config import HISTORY_LIMIT, MODEL, RAW_TEXT_LIMIT, get_groq_api_key
from app.schemas import Resume

resume_schema = Resume.model_json_schema()


def _get_client() -> Groq:
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Add it to backend/.env before using the AI features."
        )
    return Groq(api_key=api_key)


def parse_resume(resume_text: str) -> Resume:
    """Resume text -> structured Resume object."""
    system_prompt = f"""
    You are an expert resume parser.

    Extract information from the resume based on its meaning,
    not only based on exact section headings.

    Different resumes may use different headings, e.g.
    Experience, Professional Experience, Work History, Employment, Internships.
    These may all contain relevant experience.

    Skills may appear in the skills section, work experience,
    internships or projects.

    Return ONLY valid JSON matching this schema:

    {resume_schema}

    Important rules:
    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    """
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse the following resume:\n\n{resume_text}"},
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return Resume(**data)


def build_system_prompt(mode: str, resume: Resume, raw_text: str) -> str:
    resume_json = resume.model_dump_json(indent=2)

    if mode == "interview":
        return f"""
        You are an AI assistant representing a job candidate.
        Below is everything you know about the candidate.
        {resume_json}

        Rules:
        1. Answer only using this information.
        2. Never hallucinate.
        3. If information is unavailable, say "I don't know".
        4. Be professional.
        5. Answer as if an HR person is interviewing this candidate.
        """

    return f"""
    You are an expert resume analyzer and career coach.
    The user has uploaded their resume. Help them improve it.

    Structured data extracted from the resume:
    {resume_json}

    Raw resume text (for judging wording, formatting and content quality):
    {raw_text[:RAW_TEXT_LIMIT]}

    Rules:
    1. Base every observation on the resume above. Never invent experience, skills or numbers.
    2. When asked to analyze, cover: strengths, weaknesses/gaps, ATS-friendliness,
       missing keywords for the target role, and concrete rewrite suggestions.
    3. Give specific, actionable advice (show before/after bullet rewrites when useful).
    4. If something is not in the resume, say so instead of guessing.
    5. Use Markdown (headings, bullet points) and keep answers focused.
    """


def answer_question(
    question: str, mode: str, resume: Resume, raw_text: str, history: list[dict]
) -> str:
    messages = [{"role": "system", "content": build_system_prompt(mode, resume, raw_text)}]
    for m in history[-HISTORY_LIMIT:]:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": question})

    response = _get_client().chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content
