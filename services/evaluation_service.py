import json
import re
from datetime import datetime
from models import db, Interview, Question, Answer, Evaluation, Report, CandidateProfile
from services.ai_service import evaluate_answer, generate_final_report

def save_answer_and_evaluate(question_id, answer_text, duration_seconds, profile, role_name):
    """Save answer, run evaluation, persist to DB."""
    from models import Answer, Evaluation, Question
    question = db.session.get(Question, question_id)
    if not question:
        return None

    filler_data = _count_fillers(answer_text)

    answer = Answer(
        question_id=question_id,
        answer_text=answer_text,
        duration_seconds=duration_seconds,
        filler_words=json.dumps(filler_data)
    )
    db.session.add(answer)
    db.session.flush()

    eval_data = evaluate_answer(question.question_text, answer_text, profile, role_name)

    evaluation = Evaluation(
        answer_id=answer.id,
        relevance_score=eval_data.get('relevance_score', 7),
        clarity_score=eval_data.get('clarity_score', 7),
        completeness_score=eval_data.get('completeness_score', 7),
        structure_score=eval_data.get('structure_score', 7),
        overall_score=eval_data.get('overall_score', 7),
        star_situation=eval_data.get('star_situation', 'N/A'),
        star_task=eval_data.get('star_task', 'N/A'),
        star_action=eval_data.get('star_action', 'N/A'),
        star_result=eval_data.get('star_result', 'N/A'),
        strengths=eval_data.get('strengths', ''),
        improvements=eval_data.get('improvements', ''),
        eval_json=json.dumps(eval_data)
    )
    db.session.add(evaluation)
    db.session.commit()
    return eval_data


def build_final_report(interview_id):
    """Compile all evaluations into a final report."""
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return None

    profile = {}
    if interview.profile_id:
        cp = db.session.get(CandidateProfile, interview.profile_id)
        if cp and cp.profile_json:
            profile = json.loads(cp.profile_json)

    role_name = ''
    if interview.role_id:
        from models import Role
        role = db.session.get(Role, interview.role_id)
        if role:
            role_name = role.name

    evaluations = []
    for q in interview.questions:
        if q.answer and q.answer.evaluation:
            ev = q.answer.evaluation
            evaluations.append(json.loads(ev.eval_json) if ev.eval_json else {})

    report_data = generate_final_report(
        profile, role_name, interview.mode, interview.difficulty,
        evaluations, []
    )

    report = Report.query.filter_by(interview_id=interview_id).first()
    if not report:
        report = Report(interview_id=interview_id)
        db.session.add(report)

    report.overall_score = report_data.get('overall_score', 70)
    report.communication_score = report_data.get('communication_score', 70)
    report.answer_quality_score = report_data.get('answer_quality_score', 70)
    report.relevance_score = report_data.get('relevance_score', 70)
    report.clarity_score = report_data.get('clarity_score', 70)
    report.structure_score = report_data.get('structure_score', 70)
    report.star_score = report_data.get('star_score', 60)
    report.hr_readiness_score = report_data.get('hr_readiness_score', 70)
    report.strengths = json.dumps(report_data.get('strengths', []))
    report.improvements = json.dumps(report_data.get('improvements', []))
    report.improvement_plan = json.dumps(report_data.get('improvement_plan', []))
    report.weak_areas = json.dumps(report_data.get('weak_areas', []))
    report.report_json = json.dumps(report_data)

    interview.overall_score = report.overall_score
    interview.status = 'completed'
    interview.completed_at = datetime.utcnow()
    db.session.commit()
    return report


def get_conversation_history(interview_id):
    """Return list of {question, answer} dicts for AI context."""
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return []
    history = []
    for q in sorted(interview.questions, key=lambda x: x.question_number or 0):
        answer_text = q.answer.answer_text if q.answer else ''
        history.append({'question': q.question_text, 'answer': answer_text or ''})
    return history


def _count_fillers(text):
    if not text:
        return {}
    fillers = ['um', 'uh', 'like', 'actually', 'you know', 'basically',
               'literally', 'kind of', 'sort of', 'i mean', 'right']
    text_lower = text.lower()
    found = {}
    for f in fillers:
        count = len(re.findall(r'\b' + re.escape(f) + r'\b', text_lower))
        if count > 0:
            found[f] = count
    return found
