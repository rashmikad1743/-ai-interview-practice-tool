from concurrent.futures import ThreadPoolExecutor

from django.db import close_old_connections
from django.utils import timezone

from interview.models import InterviewSession, TechnicalResponse
from interview.services.resume_ai import (
    extract_resume_role_match,
    generate_role_based_questions,
)


_EXECUTOR = ThreadPoolExecutor(max_workers=2)


def _run_precompute(session_id, resume_text, fallback_role='PYTHON', question_count=20):
    close_old_connections()
    try:
        session = InterviewSession.objects.select_related('user').get(id=session_id)
    except InterviewSession.DoesNotExist:
        close_old_connections()
        return

    technical_response, _ = TechnicalResponse.objects.get_or_create(session=session)
    match_payload = extract_resume_role_match(resume_text)
    best_role = match_payload.get('best_role') or fallback_role or 'PYTHON'

    questions = generate_role_based_questions(
        resume_text=resume_text,
        target_role=best_role,
        exclude_questions=[],
        question_count=question_count,
    )

    technical_response.target_role = best_role
    technical_response.resume_text = resume_text
    technical_response.generated_questions = questions
    technical_response.interviewer_notes = (
        f"Pre-generated at {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Role: {best_role} | Keywords: {', '.join(match_payload.get('keywords', [])[:8])}"
    )
    technical_response.save(update_fields=['target_role', 'resume_text', 'generated_questions', 'interviewer_notes', 'updated_at'])
    close_old_connections()


def queue_technical_questions_precompute(session_id, resume_text, fallback_role='PYTHON', question_count=20):
    if not (resume_text or '').strip():
        return
    _EXECUTOR.submit(_run_precompute, session_id, resume_text, fallback_role, question_count)
