import json
import os
from config import Config

# ── Demo data ──────────────────────────────────────────────────────────────────
DEMO_PROFILE = {
    "name": "Alex Johnson",
    "education": "B.Tech Computer Science, XYZ University (2024)",
    "skills": ["Communication", "Problem Solving", "Teamwork", "Leadership"],
    "technical_skills": ["Python", "JavaScript", "SQL", "React"],
    "projects": ["E-Commerce Website using Python/Django", "Student Management System"],
    "internships": ["Web Development Intern at TechCorp (3 months)"],
    "experience": "Fresher with internship experience",
    "certifications": ["Python for Data Science - Coursera"],
    "achievements": ["Hackathon Winner 2023", "Academic Excellence Award"],
    "career_objective": "Seeking a challenging role in software development",
    "hobbies": ["Coding", "Reading tech blogs"],
    "leadership": ["Led a team of 4 in final year project"],
    "teamwork": ["Collaborated on multiple group projects"]
}

DEMO_QUESTIONS = [
    {"text": "Tell me about yourself and why you are interested in this role.", "reason": "Standard opening question to understand the candidate's background.", "category": "introduction"},
    {"text": "I see you worked on an E-Commerce project. Can you walk me through your contribution?", "reason": "Resume mentions E-Commerce project — verifying the claim.", "category": "resume_based"},
    {"text": "What would you say is your greatest strength, and how has it helped you professionally?", "reason": "Assessing self-awareness and relevant strengths.", "category": "strengths"},
    {"text": "Tell me about a challenge you faced during your internship and how you handled it.", "reason": "Behavioral question to assess problem-solving.", "category": "behavioral"},
    {"text": "Where do you see yourself in 3 years?", "reason": "Assessing career goals and ambition.", "category": "career_goals"},
    {"text": "Why should we hire you over other candidates?", "reason": "Assessing confidence and value proposition.", "category": "why_hire"},
    {"text": "Describe a situation where you had to work under pressure. How did you manage it?", "reason": "Assessing stress management and adaptability.", "category": "behavioral"},
    {"text": "Do you have any questions for us?", "reason": "Standard closing question.", "category": "closing"}
]

DEMO_EVALUATION = {
    "relevance_score": 7.5,
    "clarity_score": 7.0,
    "completeness_score": 6.5,
    "structure_score": 7.0,
    "overall_score": 7.0,
    "star_situation": "Good",
    "star_task": "Good",
    "star_action": "Good",
    "star_result": "Needs improvement",
    "strengths": "Clear communication, relevant examples",
    "improvements": "Add measurable results, reduce filler words",
    "what_was_good": "You gave a clear and relevant answer.",
    "what_was_missing": "Try to include specific measurable outcomes.",
    "how_to_improve": "Use the STAR method: Situation, Task, Action, Result."
}

# ── AI client initialisation ───────────────────────────────────────────────────
def _get_ai_client():
    provider = Config.AI_PROVIDER.lower()
    if provider == 'gemini' and Config.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=Config.GEMINI_API_KEY)
        return 'gemini', genai.GenerativeModel('gemini-1.5-flash')
    if provider == 'openai' and Config.OPENAI_API_KEY:
        from openai import OpenAI
        return 'openai', OpenAI(api_key=Config.OPENAI_API_KEY)
    return 'demo', None

def _call_ai(prompt, client_info):
    provider, client = client_info
    if provider == 'gemini':
        response = client.generate_content(prompt)
        return response.text
    if provider == 'openai':
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    return None

def _parse_json_response(text):
    """Extract JSON from AI response, handling markdown code blocks."""
    if not text:
        return None
    text = text.strip()
    # Remove markdown code fences
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0].strip()
    elif '```' in text:
        text = text.split('```')[1].split('```')[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return None

# ── Public service functions ───────────────────────────────────────────────────

def analyze_resume(resume_text, role_name):
    """Extract structured profile from resume text."""
    if Config.DEMO_MODE or not resume_text.strip():
        return DEMO_PROFILE

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        return DEMO_PROFILE

    prompt = f"""You are an expert HR resume analyst. Analyze the following resume for a {role_name} position.
Extract information and return ONLY a valid JSON object with these exact keys:
{{
  "name": "candidate full name or empty string",
  "education": "education details as string",
  "skills": ["skill1", "skill2"],
  "technical_skills": ["tech1", "tech2"],
  "projects": ["project description 1", "project description 2"],
  "internships": ["internship 1"],
  "experience": "work experience summary",
  "certifications": ["cert1"],
  "achievements": ["achievement1"],
  "career_objective": "career objective text",
  "hobbies": ["hobby1"],
  "leadership": ["leadership example"],
  "teamwork": ["teamwork example"]
}}

Resume:
{resume_text[:4000]}

Return ONLY the JSON object, no explanation."""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if parsed:
            return parsed
    except Exception:
        pass
    return DEMO_PROFILE


def create_candidate_profile(profile_data, role_name):
    """Return a display-ready summary string."""
    name = profile_data.get('name', 'Candidate')
    skills = ', '.join(profile_data.get('technical_skills', []) + profile_data.get('skills', []))
    projects = '; '.join(profile_data.get('projects', []))
    return f"Name: {name} | Role: {role_name} | Skills: {skills} | Projects: {projects}"


def generate_initial_question(profile, role_name, mode, difficulty, style):
    """Generate the first interview question."""
    if Config.DEMO_MODE:
        q = DEMO_QUESTIONS[0]
        return {"text": q["text"], "reason": q["reason"], "category": q["category"]}

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        q = DEMO_QUESTIONS[0]
        return {"text": q["text"], "reason": q["reason"], "category": q["category"]}

    profile_summary = json.dumps(profile, indent=2)[:2000]
    prompt = f"""You are an AI HR interviewer conducting a {mode} interview for a {role_name} position.
Difficulty: {difficulty}. Interviewer style: {style}.

Candidate profile:
{profile_summary}

Generate the FIRST interview question. It should be personalized based on the candidate's background.
Return ONLY a JSON object:
{{
  "text": "the interview question",
  "reason": "why you are asking this (1 sentence, mention resume detail if applicable)",
  "category": "introduction/resume_based/behavioral/strengths/career_goals/etc"
}}"""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if parsed and 'text' in parsed:
            return parsed
    except Exception:
        pass
    return {"text": DEMO_QUESTIONS[0]["text"], "reason": DEMO_QUESTIONS[0]["reason"], "category": "introduction"}


def generate_followup_question(profile, role_name, mode, difficulty, style,
                                conversation_history, question_number, total_questions):
    """Generate next question based on full conversation history."""
    if Config.DEMO_MODE:
        idx = min(question_number, len(DEMO_QUESTIONS) - 1)
        q = DEMO_QUESTIONS[idx]
        return {"text": q["text"], "reason": q["reason"], "category": q["category"]}

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        idx = min(question_number, len(DEMO_QUESTIONS) - 1)
        q = DEMO_QUESTIONS[idx]
        return {"text": q["text"], "reason": q["reason"], "category": q["category"]}

    profile_summary = json.dumps(profile, indent=2)[:1500]
    history_text = '\n'.join(
        [f"Q{i+1}: {h['question']}\nA{i+1}: {h['answer']}" for i, h in enumerate(conversation_history)]
    )

    prompt = f"""You are an AI HR interviewer. This is question {question_number + 1} of {total_questions}.
Role: {role_name} | Mode: {mode} | Difficulty: {difficulty} | Style: {style}

Candidate profile:
{profile_summary}

Conversation so far:
{history_text}

Generate the NEXT interview question. Rules:
1. Base it on the candidate's LAST answer — ask a natural follow-up OR move to a new HR topic
2. Reference specific resume details when relevant
3. Do NOT repeat previous questions
4. Cover diverse HR areas across the interview
5. For the last 2 questions, start wrapping up (career goals, closing questions)

Return ONLY JSON:
{{
  "text": "the next question",
  "reason": "why you are asking this",
  "category": "category name"
}}"""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if parsed and 'text' in parsed:
            return parsed
    except Exception:
        pass
    idx = min(question_number, len(DEMO_QUESTIONS) - 1)
    q = DEMO_QUESTIONS[idx]
    return {"text": q["text"], "reason": q["reason"], "category": q["category"]}


def evaluate_answer(question_text, answer_text, profile, role_name):
    """Evaluate a single answer and return scores + feedback."""
    if not answer_text or len(answer_text.strip()) < 5:
        return {**DEMO_EVALUATION, "overall_score": 0,
                "what_was_good": "No answer provided.",
                "what_was_missing": "Please provide a verbal answer.",
                "how_to_improve": "Speak clearly into the microphone."}

    if Config.DEMO_MODE:
        return DEMO_EVALUATION

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        return DEMO_EVALUATION

    prompt = f"""You are an expert HR evaluator. Evaluate this interview answer.

Role: {role_name}
Question: {question_text}
Answer: {answer_text}

Candidate background: {json.dumps(profile)[:500]}

Evaluate and return ONLY JSON:
{{
  "relevance_score": 0-10,
  "clarity_score": 0-10,
  "completeness_score": 0-10,
  "structure_score": 0-10,
  "overall_score": 0-10,
  "star_situation": "Good/Partial/Missing/N/A",
  "star_task": "Good/Partial/Missing/N/A",
  "star_action": "Good/Partial/Missing/N/A",
  "star_result": "Good/Partial/Missing/N/A",
  "strengths": "1-2 sentence strengths",
  "improvements": "1-2 sentence improvements",
  "what_was_good": "specific positive feedback",
  "what_was_missing": "specific gap",
  "how_to_improve": "actionable tip"
}}"""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if parsed and 'overall_score' in parsed:
            return parsed
    except Exception:
        pass
    return DEMO_EVALUATION


def generate_final_report(profile, role_name, mode, difficulty, evaluations, conversation_history):
    """Generate the complete final HR report."""
    if not evaluations:
        return _build_demo_report(profile, role_name, mode, difficulty)

    avg_scores = {
        'overall': sum(e.get('overall_score', 7) for e in evaluations) / len(evaluations),
        'relevance': sum(e.get('relevance_score', 7) for e in evaluations) / len(evaluations),
        'clarity': sum(e.get('clarity_score', 7) for e in evaluations) / len(evaluations),
        'completeness': sum(e.get('completeness_score', 7) for e in evaluations) / len(evaluations),
        'structure': sum(e.get('structure_score', 7) for e in evaluations) / len(evaluations),
    }

    if Config.DEMO_MODE:
        return _build_demo_report(profile, role_name, mode, difficulty, avg_scores)

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        return _build_demo_report(profile, role_name, mode, difficulty, avg_scores)

    eval_summary = json.dumps(evaluations[:5], indent=2)[:2000]
    prompt = f"""You are an expert HR coach. Generate a final interview performance report.

Candidate: {profile.get('name', 'Candidate')} | Role: {role_name} | Mode: {mode}
Average scores: {json.dumps(avg_scores)}
Evaluations summary: {eval_summary}

Return ONLY JSON:
{{
  "overall_score": 0-100,
  "communication_score": 0-100,
  "answer_quality_score": 0-100,
  "hr_readiness_score": 0-100,
  "star_score": 0-100,
  "strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "improvement_plan": ["action1", "action2", "action3"],
  "weak_areas": ["area1", "area2"],
  "summary": "2-3 sentence overall assessment"
}}"""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if parsed and 'overall_score' in parsed:
            parsed['relevance_score'] = round(avg_scores['relevance'] * 10)
            parsed['clarity_score'] = round(avg_scores['clarity'] * 10)
            parsed['structure_score'] = round(avg_scores['structure'] * 10)
            return parsed
    except Exception:
        pass
    return _build_demo_report(profile, role_name, mode, difficulty, avg_scores)


def generate_weak_area_questions(profile, role_name, weak_areas, count=5):
    """Generate targeted practice questions for weak areas."""
    if Config.DEMO_MODE or not weak_areas:
        return [{"text": q["text"], "reason": q["reason"], "category": q["category"]}
                for q in DEMO_QUESTIONS[:count]]

    client_info = _get_ai_client()
    if client_info[0] == 'demo':
        return [{"text": q["text"], "reason": q["reason"], "category": q["category"]}
                for q in DEMO_QUESTIONS[:count]]

    prompt = f"""Generate {count} targeted HR interview practice questions for weak areas.
Role: {role_name}
Weak areas: {', '.join(weak_areas)}
Candidate profile: {json.dumps(profile)[:500]}

Return ONLY a JSON array:
[
  {{"text": "question", "reason": "why this helps", "category": "category"}},
  ...
]"""

    try:
        result = _call_ai(prompt, client_info)
        parsed = _parse_json_response(result)
        if isinstance(parsed, list) and parsed:
            return parsed[:count]
    except Exception:
        pass
    return [{"text": q["text"], "reason": q["reason"], "category": q["category"]}
            for q in DEMO_QUESTIONS[:count]]


def _build_demo_report(profile, role_name, mode, difficulty, avg_scores=None):
    base = avg_scores['overall'] * 10 if avg_scores else 72
    return {
        "overall_score": round(base),
        "communication_score": round(base + 5),
        "answer_quality_score": round(base - 3),
        "hr_readiness_score": round(base + 2),
        "star_score": round(base - 8),
        "relevance_score": round(avg_scores['relevance'] * 10) if avg_scores else 75,
        "clarity_score": round(avg_scores['clarity'] * 10) if avg_scores else 70,
        "structure_score": round(avg_scores['structure'] * 10) if avg_scores else 68,
        "strengths": [
            "Good communication and clear articulation",
            "Relevant examples from resume and projects",
            "Positive attitude and enthusiasm for the role"
        ],
        "improvements": [
            "Add measurable results to behavioral answers",
            "Improve STAR structure in situational responses",
            "Reduce filler words for more confident delivery"
        ],
        "improvement_plan": [
            "Practice STAR method with 3 examples from your projects",
            "Record yourself answering questions to identify filler words",
            "Research the company and role before each interview",
            "Prepare 2-3 specific achievement stories with numbers"
        ],
        "weak_areas": ["STAR structure", "Quantified results"],
        "summary": f"You showed good potential for the {role_name} role. Focus on structuring behavioral answers using the STAR method and quantifying your achievements for stronger impact."
    }
