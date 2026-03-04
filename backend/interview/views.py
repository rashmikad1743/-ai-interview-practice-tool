from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import re
import os

from .management.commands.seed_aptitude_questions import AI_GENERATED_QUESTIONS
from .management.commands.seed_coding_questions import CODING_SKELETON_QUESTIONS
from .models import (
	AptitudeQuestion,
	AptitudeResponse,
	AptitudeSessionQuestion,
	CodingQuestion,
	CodingResponse,
	CodingSessionQuestion,
	HRResponse,
	InterviewSession,
	StageResult,
	TechnicalResponse,
)
from .services.code_runner import evaluate_coding_submission, run_code
from .services.question_precompute import queue_technical_questions_precompute
from .services.report_pdf import build_session_report_pdf
from .services.resume_ai import (
	extract_resume_role_match,
	generate_role_based_questions,
)


APTITUDE_QUESTION_COUNT = 30
APTITUDE_DURATION_MINUTES = 20
CODING_QUESTION_COUNT = 3
CODING_DURATION_MINUTES = 30
TECHNICAL_DURATION_MINUTES = 30

TECHNICAL_ROLE_KEYWORDS = {
	TechnicalResponse.RoleTrack.AIML: ['ml', 'model', 'training', 'feature', 'dataset', 'inference', 'evaluation', 'drift', 'pipeline'],
	TechnicalResponse.RoleTrack.WEB_DEV: ['api', 'frontend', 'backend', 'database', 'auth', 'security', 'deployment', 'cache'],
	TechnicalResponse.RoleTrack.UI_UX: ['user', 'research', 'wireframe', 'prototype', 'usability', 'accessibility', 'design', 'persona'],
	TechnicalResponse.RoleTrack.FRONTEND: ['html', 'css', 'javascript', 'react', 'component', 'state', 'responsive', 'dom'],
	TechnicalResponse.RoleTrack.BACKEND: ['api', 'database', 'query', 'auth', 'service', 'scaling', 'queue', 'cache'],
	TechnicalResponse.RoleTrack.FULL_STACK: ['frontend', 'backend', 'api', 'database', 'integration', 'deployment', 'debugging', 'architecture'],
	TechnicalResponse.RoleTrack.MERN_STACK: ['mongodb', 'express', 'react', 'node', 'mongoose', 'jwt', 'middleware', 'schema'],
	TechnicalResponse.RoleTrack.DEVOPS: ['ci', 'cd', 'pipeline', 'docker', 'kubernetes', 'terraform', 'monitoring', 'incident'],
	TechnicalResponse.RoleTrack.DATA_ANALYST: ['sql', 'dashboard', 'kpi', 'analysis', 'report', 'cohort', 'funnel', 'insight'],
	TechnicalResponse.RoleTrack.DATA_SCIENTIST: ['model', 'feature', 'training', 'validation', 'drift', 'experiment', 'dataset', 'inference'],
	TechnicalResponse.RoleTrack.QA_AUTOMATION: ['test', 'automation', 'selenium', 'playwright', 'regression', 'api', 'coverage', 'flaky'],
	TechnicalResponse.RoleTrack.CYBERSECURITY: ['security', 'threat', 'vulnerability', 'encryption', 'iam', 'incident', 'siem', 'zero-trust'],
	TechnicalResponse.RoleTrack.CLOUD_ENGINEER: ['cloud', 'aws', 'azure', 'gcp', 'vpc', 'autoscaling', 'iac', 'cost'],
	TechnicalResponse.RoleTrack.ANDROID: ['android', 'activity', 'mvvm', 'room', 'workmanager', 'kotlin', 'lifecycle', 'playstore'],
	TechnicalResponse.RoleTrack.IOS: ['ios', 'swift', 'viewcontroller', 'coredata', 'async', 'keychain', 'xcode', 'appstore'],
	TechnicalResponse.RoleTrack.PHP: ['php', 'composer', 'laravel', 'symfony', 'session', 'mysql', 'mvc', 'routing'],
	TechnicalResponse.RoleTrack.JAVASCRIPT: ['javascript', 'event', 'promise', 'async', 'closure', 'prototype', 'state', 'render'],
	TechnicalResponse.RoleTrack.PYTHON: ['python', 'asyncio', 'decorator', 'package', 'typing', 'django', 'fastapi', 'profiling'],
	TechnicalResponse.RoleTrack.GEN_AI: ['llm', 'prompt', 'rag', 'embedding', 'token', 'hallucination', 'inference', 'guardrail'],
	TechnicalResponse.RoleTrack.JAVA: ['java', 'spring', 'jpa', 'thread', 'transaction', 'microservice', 'gc', 'exception'],
	TechnicalResponse.RoleTrack.ANGULAR: ['angular', 'component', 'rxjs', 'observable', 'change', 'module', 'service', 'router'],
	TechnicalResponse.RoleTrack.DOTNET: ['dotnet', 'aspnet', 'entity', 'middleware', 'dependency', 'async', 'csharp', 'api'],
}

TECHNICAL_STOPWORDS = {
	'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'has', 'had', 'you', 'your', 'our',
	'are', 'was', 'were', 'not', 'but', 'into', 'over', 'under', 'when', 'where', 'what', 'which',
	'they', 'them', 'their', 'will', 'would', 'can', 'could', 'should', 'about', 'there', 'here',
}

STAGE_ORDER = [
	(StageResult.StageName.APTITUDE, 'Stage 1 — Aptitude'),
	(StageResult.StageName.CODING, 'Stage 2 — Coding'),
	(StageResult.StageName.TECHNICAL, 'Stage 3 — Technical'),
	(StageResult.StageName.HR, 'Stage 4 — HR'),
]


def _is_serverless_read_only_media():
	return bool(os.getenv('VERCEL'))

STAGE_ROUTE_MAP = {
	StageResult.StageName.APTITUDE: 'interview:aptitude_round',
	StageResult.StageName.CODING: 'interview:coding_round',
	StageResult.StageName.TECHNICAL: 'interview:technical_round',
	StageResult.StageName.HR: 'interview:hr_round',
}

STAGE_RESULT_ROUTE_MAP = {
	StageResult.StageName.APTITUDE: 'interview:aptitude_result',
	StageResult.StageName.CODING: 'interview:coding_result',
	StageResult.StageName.TECHNICAL: 'interview:technical_result',
	StageResult.StageName.HR: 'interview:hr_result',
}

HR_QUESTIONS = [
	'Tell me about yourself.',
	'Why do you want to work for this company?',
	'Why are you looking for a change/leaving your current job?',
	'What are your greatest strengths?',
	'What is your greatest weakness?',
	'Why should we hire you?',
	'Where do you see yourself in 5 years?',
	'Tell me about a time you handled a workplace conflict/challenge.',
	'How do you handle stress and pressure?',
	'What are your salary expectations?',
	'Are you willing to relocate or travel?',
	'What do you know about our company?',
	'How do you define success?',
	'Tell me about a time you failed.',
	'What motivates you to do a good job?',
	'What is your management style (if applicable)?',
	'How do you prioritize your work?',
	'What sets you apart from other candidates?',
	'What is your ideal work environment?',
	'Do you have any questions for me?',
]


def _next_stage_route_name(session):
	completed_results = StageResult.objects.filter(session=session, is_completed=True)
	completed_set = {item.stage_name for item in completed_results}

	for stage_name, _ in STAGE_ORDER:
		if stage_name in completed_set:
			continue
		route = STAGE_ROUTE_MAP.get(stage_name)
		if route:
			return route

	return None


def _build_stage_progress(session):
	completed_results = StageResult.objects.filter(session=session, is_completed=True)
	result_map = {item.stage_name: item for item in completed_results}
	completed_set = set(result_map.keys())

	progress_rows = []
	for index, (stage_name, stage_label) in enumerate(STAGE_ORDER):
		result = result_map.get(stage_name)
		is_completed = bool(result)

		previous_stages_completed = all(
			previous_stage_name in completed_set
			for previous_stage_name, _ in STAGE_ORDER[:index]
		)

		action_url = None
		action_label = None
		action_hint = ''

		if is_completed:
			result_route = STAGE_RESULT_ROUTE_MAP.get(stage_name)
			if result_route:
				action_url = reverse(result_route, args=[session.id])
				action_label = 'View Result'
			else:
				action_hint = 'Result view will be added soon.'
		else:
			round_route = STAGE_ROUTE_MAP.get(stage_name)
			if round_route and previous_stages_completed:
				action_url = reverse(round_route, args=[session.id])
				action_label = 'Start / Resume'
			elif round_route and not previous_stages_completed:
				action_hint = 'Complete previous stage first.'
			else:
				action_hint = 'Coming soon.'

		progress_rows.append(
			{
				'stage_name': stage_name,
				'stage_label': stage_label,
				'is_completed': is_completed,
				'score': result.score if result else None,
				'feedback': result.feedback if result else '',
				'action_url': action_url,
				'action_label': action_label,
				'action_hint': action_hint,
			}
		)

	completed_count = sum(1 for row in progress_rows if row['is_completed'])
	return progress_rows, completed_count


def _recalculate_session_weighted_score(session):
	completed_results = StageResult.objects.filter(session=session, is_completed=True)
	if not completed_results.exists():
		return

	score_sum = sum(float(item.score) for item in completed_results)
	weighted = round(score_sum / completed_results.count(), 2)
	session.weighted_score = weighted
	session.save(update_fields=['weighted_score'])


@login_required
def dashboard_view(request):
	in_progress_sessions = InterviewSession.objects.filter(
		user=request.user,
		status=InterviewSession.SessionStatus.IN_PROGRESS,
	)
	completed_sessions = InterviewSession.objects.filter(
		user=request.user,
		status=InterviewSession.SessionStatus.COMPLETED,
	)
	return render(
		request,
		'interview/dashboard.html',
		{
			'in_progress_sessions': in_progress_sessions,
			'completed_sessions': completed_sessions,
		},
	)


@login_required
def start_interview_view(request):
	resume_text = (request.session.get('login_resume_text') or '').strip()
	best_role = request.session.get('login_best_role') or 'PYTHON'

	if not resume_text:
		messages.warning(request, 'Please login again and upload resume first to start interview flow.')
		return redirect('accounts:login')

	session = InterviewSession.objects.create(user=request.user, title='New Interview Session')
	technical_response, _ = TechnicalResponse.objects.get_or_create(session=session)
	technical_response.resume_text = resume_text
	technical_response.target_role = best_role
	technical_response.generated_questions = []
	technical_response.interviewer_notes = 'Background generation in progress while you complete aptitude and coding rounds.'
	technical_response.save(update_fields=['resume_text', 'target_role', 'generated_questions', 'interviewer_notes', 'updated_at'])

	queue_technical_questions_precompute(
		session_id=session.id,
		resume_text=resume_text,
		fallback_role=best_role,
		question_count=20,
	)

	messages.success(request, f'New interview session started (Session #{session.id}).')
	return redirect('interview:aptitude_round', session_id=session.id)


@login_required
def resume_interview_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	if session.status != InterviewSession.SessionStatus.IN_PROGRESS:
		messages.warning(request, 'Only in-progress sessions can be resumed.')
		return redirect('interview:dashboard')

	next_route = _next_stage_route_name(session)
	if not next_route:
		messages.info(request, 'Implemented stages are complete for this session. See overall progress below.')
		return redirect('interview:session_progress', session_id=session.id)

	if next_route == 'interview:aptitude_round':
		messages.info(request, f'Resumed Session #{session.id} (Aptitude Round).')
		return redirect(next_route, session_id=session.id)
	if next_route == 'interview:coding_round':
		messages.info(request, f'Resumed Session #{session.id} (Coding Round).')
		return redirect(next_route, session_id=session.id)
	if next_route == 'interview:technical_round':
		messages.info(request, f'Resumed Session #{session.id} (Technical Round).')
		return redirect(next_route, session_id=session.id)
	if next_route == 'interview:hr_round':
		messages.info(request, f'Resumed Session #{session.id} (HR Round).')
		return redirect(next_route, session_id=session.id)

	return redirect('interview:session_progress', session_id=session.id)


@login_required
def session_progress_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	progress_rows, completed_count = _build_stage_progress(session)
	next_route = _next_stage_route_name(session)
	next_label = None
	if next_route == 'interview:aptitude_round':
		next_label = 'Continue Stage 1 — Aptitude'
	elif next_route == 'interview:coding_round':
		next_label = 'Continue Stage 2 — Coding'
	elif next_route == 'interview:technical_round':
		next_label = 'Continue Stage 3 — Technical'
	elif next_route == 'interview:hr_round':
		next_label = 'Continue Stage 4 — HR'

	context = {
		'session': session,
		'progress_rows': progress_rows,
		'completed_count': completed_count,
		'total_stages': len(STAGE_ORDER),
		'next_route': next_route,
		'next_label': next_label,
	}
	return render(request, 'interview/session_progress.html', context)


@login_required
def reports_view(request):
	sessions = InterviewSession.objects.filter(user=request.user)
	stage_results = StageResult.objects.filter(session__in=sessions, is_completed=True)
	result_map = {}
	for result in stage_results:
		result_map.setdefault(result.session_id, {})[result.stage_name] = result

	report_rows = [
		{
			'session': session,
			'aptitude_result': result_map.get(session.id, {}).get(StageResult.StageName.APTITUDE),
			'coding_result': result_map.get(session.id, {}).get(StageResult.StageName.CODING),
			'technical_result': result_map.get(session.id, {}).get(StageResult.StageName.TECHNICAL),
			'hr_result': result_map.get(session.id, {}).get(StageResult.StageName.HR),
		}
		for session in sessions
	]
	return render(
		request,
		'interview/reports.html',
		{
			'report_rows': report_rows,
		},
	)


def _build_overall_result_context(session):
	result_map = {
		result.stage_name: result
		for result in StageResult.objects.filter(session=session, is_completed=True)
	}

	stage_rows = []
	available_scores = []
	for stage_name, stage_label in STAGE_ORDER:
		result = result_map.get(stage_name)
		score = float(result.score) if result else None
		if score is not None:
			available_scores.append(score)

		stage_rows.append(
			{
				'stage_name': stage_name,
				'stage_label': stage_label,
				'score': score,
				'is_completed': bool(result),
			}
		)

	overall_score = round(sum(available_scores) / len(available_scores), 2) if available_scores else 0.0
	completed_stages = sum(1 for row in stage_rows if row['is_completed'])
	is_finalized = completed_stages == len(STAGE_ORDER)

	if overall_score >= 80:
		overall_grade = 'Excellent'
		readiness = 'Interview-ready'
	elif overall_score >= 65:
		overall_grade = 'Good'
		readiness = 'Almost ready'
	elif overall_score >= 50:
		overall_grade = 'Average'
		readiness = 'Needs targeted practice'
	else:
		overall_grade = 'Beginner'
		readiness = 'Needs strong improvement'

	completed_rows = [row for row in stage_rows if row['score'] is not None]
	completed_rows_sorted = sorted(completed_rows, key=lambda item: item['score'], reverse=True)
	strengths = [item['stage_label'] for item in completed_rows_sorted[:2]]
	improvements = [item['stage_label'] for item in completed_rows_sorted[-2:]] if completed_rows_sorted else []

	summary = (
		f'Overall Score: {overall_score}% ({overall_grade}). '
		f'Readiness: {readiness}. '
		f'Completed {completed_stages}/{len(STAGE_ORDER)} rounds.'
	)

	return {
		'stage_rows': stage_rows,
		'overall_score': overall_score,
		'overall_grade': overall_grade,
		'readiness': readiness,
		'is_finalized': is_finalized,
		'completed_stages': completed_stages,
		'total_stages': len(STAGE_ORDER),
		'strengths': strengths,
		'improvements': improvements,
		'summary': summary,
	}


def _ensure_aptitude_questions_for_session(session):
	existing = AptitudeSessionQuestion.objects.filter(session=session).count()
	if existing > 0:
		return

	if not AptitudeQuestion.objects.filter(is_active=True).exists():
		for item in AI_GENERATED_QUESTIONS:
			AptitudeQuestion.objects.get_or_create(
				question_text=item['question_text'],
				defaults=item,
			)

	seen_question_ids = AptitudeSessionQuestion.objects.filter(
		session__user=session.user,
	).exclude(
		session=session,
	).values_list('question_id', flat=True)

	question_ids = list(
		AptitudeQuestion.objects.filter(is_active=True)
		.exclude(id__in=seen_question_ids)
		.values_list('id', flat=True)
		.order_by('?')[:APTITUDE_QUESTION_COUNT]
	)

	if len(question_ids) < APTITUDE_QUESTION_COUNT:
		remaining = APTITUDE_QUESTION_COUNT - len(question_ids)
		fallback_ids = list(
			AptitudeQuestion.objects.filter(is_active=True)
			.exclude(id__in=question_ids)
			.values_list('id', flat=True)
			.order_by('?')[:remaining]
		)
		question_ids.extend(fallback_ids)

	if not question_ids:
		return

	for order_index, question_id in enumerate(question_ids, start=1):
		AptitudeSessionQuestion.objects.create(
			session=session,
			question_id=question_id,
			display_order=order_index,
		)


def _finalize_aptitude_round(session, session_questions, post_data):
	correct_answers = 0
	attempted_answers = 0

	for session_question in session_questions:
		key = f'answer_{session_question.id}'
		selected_option = post_data.get(key) if post_data else None
		if selected_option not in {'A', 'B', 'C', 'D'}:
			continue

		is_correct = selected_option == session_question.question.correct_option
		if is_correct:
			correct_answers += 1
		attempted_answers += 1

		AptitudeResponse.objects.update_or_create(
			session_question=session_question,
			defaults={
				'selected_option': selected_option,
				'is_correct': is_correct,
			},
		)

	total_questions = session_questions.count()
	score = round((correct_answers / total_questions) * 100, 2) if total_questions else 0

	feedback = (
		f'Attempted {attempted_answers}/{total_questions} questions. '
		f'Correct answers: {correct_answers}. Aptitude score: {score}%.'
	)

	StageResult.objects.update_or_create(
		session=session,
		stage_name=StageResult.StageName.APTITUDE,
		defaults={
			'score': score,
			'max_score': 100,
			'feedback': feedback,
			'is_completed': True,
		},
	)

	session.overall_feedback = feedback
	session.save(update_fields=['overall_feedback'])
	_recalculate_session_weighted_score(session)

	return score


def _ensure_coding_questions_for_session(session):
	existing = CodingSessionQuestion.objects.filter(session=session).count()
	if existing > 0:
		return

	if not CodingQuestion.objects.filter(is_active=True).exists():
		for item in CODING_SKELETON_QUESTIONS:
			CodingQuestion.objects.get_or_create(
				title=item['title'],
				defaults=item,
			)

	seen_question_ids = CodingSessionQuestion.objects.filter(
		session__user=session.user,
	).exclude(
		session=session,
	).values_list('question_id', flat=True)

	easy_ids = list(
		CodingQuestion.objects.filter(is_active=True, difficulty=CodingQuestion.Difficulty.EASY)
		.exclude(id__in=seen_question_ids)
		.values_list('id', flat=True)
		.order_by('?')[:2]
	)
	medium_ids = list(
		CodingQuestion.objects.filter(is_active=True, difficulty=CodingQuestion.Difficulty.MEDIUM)
		.exclude(id__in=seen_question_ids)
		.values_list('id', flat=True)
		.order_by('?')[:1]
	)

	question_ids = (easy_ids + medium_ids)[:CODING_QUESTION_COUNT]
	if len(question_ids) < CODING_QUESTION_COUNT:
		remaining = CODING_QUESTION_COUNT - len(question_ids)
		fallback_ids = list(
			CodingQuestion.objects.filter(is_active=True)
			.exclude(id__in=seen_question_ids)
			.exclude(id__in=question_ids)
			.values_list('id', flat=True)
			.order_by('?')[:remaining]
		)
		question_ids.extend(fallback_ids)

	if len(question_ids) < CODING_QUESTION_COUNT:
		remaining = CODING_QUESTION_COUNT - len(question_ids)
		fallback_any_ids = list(
			CodingQuestion.objects.filter(is_active=True)
			.exclude(id__in=question_ids)
			.values_list('id', flat=True)
			.order_by('?')[:remaining]
		)
		question_ids.extend(fallback_any_ids)

	for order_index, question_id in enumerate(question_ids, start=1):
		CodingSessionQuestion.objects.create(
			session=session,
			question_id=question_id,
			display_order=order_index,
		)


def _evaluate_code_placeholder(submitted_code, question, language):
	return evaluate_coding_submission(
		language=language,
		submitted_code=submitted_code,
		test_cases=question.test_cases,
		expected_keywords=question.expected_keywords,
	)


def _format_sample_value(value):
	if isinstance(value, list):
		if all(not isinstance(item, (list, dict, tuple)) for item in value):
			return f"{len(value)}\n{' '.join(str(item) for item in value)}"
		return '\n'.join(str(item) for item in value)
	if isinstance(value, dict):
		return str(value)
	if value is None:
		return 'None'
	return str(value)


def _extract_visible_sample_case(test_cases):
	if not test_cases:
		return None

	visible = None
	for index, case in enumerate(test_cases):
		if not isinstance(case, dict):
			continue
		if case.get('visible', index == 0):
			visible = case
			break

	if not visible:
		return None

	hidden_total = sum(1 for index, case in enumerate(test_cases) if isinstance(case, dict) and not case.get('visible', index == 0))
	return {
		'sample_input': _format_sample_value(visible.get('input')),
		'sample_output': _format_sample_value(visible.get('expected')),
		'hidden_total': hidden_total,
	}


def _finalize_coding_round(session, coding_session_questions, post_data):
	total_score = 0
	attempted = 0

	for session_question in coding_session_questions:
		existing_response = CodingResponse.objects.filter(session_question=session_question).first()
		key = f'code_{session_question.id}'
		submitted_code = post_data.get(key, '').strip() if post_data else ''
		language = post_data.get(
			f'language_{session_question.id}',
			existing_response.language if existing_response else CodingResponse.ProgrammingLanguage.PYTHON,
		)
		if language not in dict(CodingResponse.ProgrammingLanguage.choices):
			language = CodingResponse.ProgrammingLanguage.PYTHON

		score, feedback = _evaluate_code_placeholder(submitted_code, session_question.question, language)
		if submitted_code:
			attempted += 1
		total_score += float(score)

		CodingResponse.objects.update_or_create(
			session_question=session_question,
			defaults={
				'language': language,
				'submitted_code': submitted_code,
				'run_status': existing_response.run_status if existing_response else CodingResponse.RunStatus.NOT_RUN,
				'run_output': existing_response.run_output if existing_response else '',
				'compile_output': existing_response.compile_output if existing_response else '',
				'score': score,
				'feedback': feedback,
			},
		)

	total_questions = coding_session_questions.count()
	stage_score = round(total_score / total_questions, 2) if total_questions else 0
	feedback = (
		f'Attempted {attempted}/{total_questions} coding questions. '
		f'Test-case/keyword evaluation score: {stage_score}%.'
	)

	StageResult.objects.update_or_create(
		session=session,
		stage_name=StageResult.StageName.CODING,
		defaults={
			'score': stage_score,
			'max_score': 100,
			'feedback': feedback,
			'is_completed': True,
		},
	)

	session.overall_feedback = feedback
	session.save(update_fields=['overall_feedback'])
	_recalculate_session_weighted_score(session)

	return stage_score


def _clamp_score(value):
	return max(0.0, min(100.0, round(float(value), 2)))


def _tokenize_text(raw_text):
	tokens = re.findall(r'[A-Za-z][A-Za-z0-9+#.]{1,30}', (raw_text or '').lower())
	return [token for token in tokens if len(token) > 2 and token not in TECHNICAL_STOPWORDS]


def _keyword_overlap_score(source_tokens, target_tokens):
	if not source_tokens or not target_tokens:
		return 0.0

	source_set = set(source_tokens)
	target_set = set(target_tokens)
	matched = len(source_set.intersection(target_set))
	return _clamp_score((matched / max(1, len(target_set))) * 100)


def _depth_score(word_count):
	if word_count <= 20:
		return 10.0
	if word_count <= 60:
		return 40.0
	if word_count <= 120:
		return 70.0
	if word_count <= 220:
		return 85.0
	return 95.0


def _communication_score(transcript_text):
	text = (transcript_text or '').strip()
	if not text:
		return 0.0

	words = text.split()
	word_count = len(words)
	sentences = [part.strip() for part in re.split(r'[.!?]+', text) if part.strip()]
	sentence_count = len(sentences)
	avg_sentence_len = word_count / max(1, sentence_count)

	filler_terms = {'um', 'uh', 'like', 'actually', 'basically'}
	filler_count = sum(1 for token in _tokenize_text(text) if token in filler_terms)
	filler_penalty = min(25.0, filler_count * 2.0)

	score = 65.0
	if 4 <= sentence_count <= 20:
		score += 15.0
	if 8 <= avg_sentence_len <= 24:
		score += 15.0
	else:
		score -= 10.0

	score -= filler_penalty
	return _clamp_score(score)


def _question_coverage_score(transcript_tokens, generated_questions):
	if not generated_questions:
		return 0.0

	transcript_set = set(transcript_tokens)
	covered = 0

	for question in generated_questions:
		question_tokens = _tokenize_text(question)
		key_terms = set(question_tokens[:6])
		if key_terms and transcript_set.intersection(key_terms):
			covered += 1

	return _clamp_score((covered / max(1, len(generated_questions))) * 100)


def _build_technical_evaluation(technical_response, transcript_text):
	transcript = (transcript_text or '').strip()
	transcript_tokens = _tokenize_text(transcript)
	word_count = len(transcript.split()) if transcript else 0

	depth = _depth_score(word_count)
	role_keywords = TECHNICAL_ROLE_KEYWORDS.get(technical_response.target_role, [])
	role_alignment = _keyword_overlap_score(transcript_tokens, role_keywords)
	resume_alignment = _keyword_overlap_score(transcript_tokens, _tokenize_text(technical_response.resume_text))
	question_coverage = _question_coverage_score(transcript_tokens, technical_response.generated_questions or [])
	communication = _communication_score(transcript)

	final_score = _clamp_score(
		(depth * 0.30)
		+ (role_alignment * 0.20)
		+ (resume_alignment * 0.20)
		+ (question_coverage * 0.20)
		+ (communication * 0.10)
	)

	feedback = (
		f'Rubric score {final_score}% | '
		f'Depth: {depth} | '
		f'Role Alignment: {role_alignment} | '
		f'Resume Alignment: {resume_alignment} | '
		f'Question Coverage: {question_coverage} | '
		f'Communication: {communication} | '
		f'Words: {word_count}.'
	)

	return final_score, feedback


def _finalize_technical_round(session, technical_response, transcript_text):
	transcript = (transcript_text or '').strip()
	score, feedback = _build_technical_evaluation(technical_response, transcript)

	technical_response.transcript = transcript
	technical_response.save(update_fields=['transcript'])

	StageResult.objects.update_or_create(
		session=session,
		stage_name=StageResult.StageName.TECHNICAL,
		defaults={
			'score': score,
			'max_score': 100,
			'feedback': feedback,
			'is_completed': True,
		},
	)

	session.overall_feedback = feedback
	session.save(update_fields=['overall_feedback'])
	_recalculate_session_weighted_score(session)

	return score


def _evaluate_hr_answers(answers_map):
	filled_answers = [value.strip() for value in answers_map.values() if (value or '').strip()]
	attempted = len(filled_answers)

	if not filled_answers:
		return 0.0, attempted, 'No HR answers submitted.'

	all_text = ' '.join(filled_answers)
	word_count = len(all_text.split())
	avg_words_per_answer = word_count / max(1, attempted)

	depth_score = _clamp_score(min(100, (avg_words_per_answer / 35) * 100))
	coverage_score = _clamp_score((attempted / len(HR_QUESTIONS)) * 100)
	communication_score = _communication_score(all_text)

	tokens = _tokenize_text(all_text)
	filler_terms = {'um', 'uh', 'like', 'actually', 'basically', 'youknow'}
	hedge_terms = {'maybe', 'probably', 'perhaps', 'guess', 'unsure', 'doubt', 'notsure'}
	assertive_terms = {'led', 'built', 'delivered', 'achieved', 'improved', 'resolved', 'managed', 'owned'}

	filler_count = sum(1 for token in tokens if token in filler_terms)
	hedge_count = sum(1 for token in tokens if token in hedge_terms)
	assertive_count = sum(1 for token in tokens if token in assertive_terms)

	confidence_score = _clamp_score(60 + (assertive_count * 3.0) - (hedge_count * 4.0) - (filler_count * 1.5))

	repeated_word_hits = len(re.findall(r'\b(\w+)\s+\1\b', all_text.lower()))
	slang_terms = {'u', 'ur', 'gonna', 'wanna', 'kinda', 'ya'}
	slang_count = sum(1 for token in re.findall(r'\b\w+\b', all_text.lower()) if token in slang_terms)

	sentence_blocks = [part.strip() for part in re.split(r'[.!?]+', all_text) if part.strip()]
	short_sentence_count = sum(1 for part in sentence_blocks if len(part.split()) < 4)
	language_mistakes = repeated_word_hits + slang_count + short_sentence_count
	language_quality_score = _clamp_score(100 - (language_mistakes * 3.5) - (filler_count * 1.2))

	final_score = _clamp_score(
		(depth_score * 0.25)
		+ (coverage_score * 0.20)
		+ (communication_score * 0.20)
		+ (confidence_score * 0.20)
		+ (language_quality_score * 0.15)
	)
	summary = (
		f'Answered {attempted}/{len(HR_QUESTIONS)} HR questions. '
		f'HR Rubric Score: {final_score}% | '
		f'Depth: {depth_score} | Coverage: {coverage_score} | Communication: {communication_score} | '
		f'Confidence: {confidence_score} | Language Quality: {language_quality_score} | '
		f'Estimated language mistakes: {language_mistakes}.'
	)

	return final_score, attempted, summary


@login_required
def aptitude_round_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

	if session.status != InterviewSession.SessionStatus.IN_PROGRESS:
		messages.info(request, 'This interview session is already closed.')
		return redirect('interview:aptitude_result', session_id=session.id)

	if StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.APTITUDE,
		is_completed=True,
	).exists():
		messages.info(request, 'Aptitude round is locked because it is already completed.')
		return redirect('interview:session_progress', session_id=session.id)

	_ensure_aptitude_questions_for_session(session)
	deadline_key = f'aptitude_deadline_{session.id}'

	deadline_timestamp = request.session.get(deadline_key)
	if not deadline_timestamp:
		deadline_timestamp = int((timezone.now() + timedelta(minutes=APTITUDE_DURATION_MINUTES)).timestamp())
		request.session[deadline_key] = deadline_timestamp

	session_questions = AptitudeSessionQuestion.objects.filter(session=session).select_related('question')
	if not session_questions.exists():
		messages.warning(
			request,
			'No aptitude questions available. Run: python manage.py seed_aptitude_questions',
		)
		return redirect('interview:dashboard')

	now_timestamp = int(timezone.now().timestamp())
	remaining_seconds = max(0, int(deadline_timestamp) - now_timestamp)

	if remaining_seconds <= 0:
		post_data = request.POST if request.method == 'POST' else {}
		score = _finalize_aptitude_round(session, session_questions, post_data)
		request.session.pop(deadline_key, None)
		messages.warning(request, f'Time is over. Aptitude round auto-submitted with score {score}%.')
		return redirect('interview:aptitude_result', session_id=session.id)

	if request.method == 'POST':
		score = _finalize_aptitude_round(session, session_questions, request.POST)
		request.session.pop(deadline_key, None)

		messages.success(
			request,
			f'Aptitude round submitted. Your score is {score}%. Stage 2 (Coding) will be enabled next.',
		)
		return redirect('interview:aptitude_result', session_id=session.id)

	return render(
		request,
		'interview/aptitude_round.html',
		{
			'session': session,
			'session_questions': session_questions,
			'remaining_seconds': remaining_seconds,
			'aptitude_duration_minutes': APTITUDE_DURATION_MINUTES,
		},
	)


@login_required
def aptitude_result_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	stage_result = get_object_or_404(
		StageResult,
		session=session,
		stage_name=StageResult.StageName.APTITUDE,
	)
	responses = AptitudeResponse.objects.filter(session_question__session=session).select_related('session_question__question')
	coding_completed = StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.CODING,
		is_completed=True,
	).exists()
	context = {
		'session': session,
		'stage_result': stage_result,
		'responses': responses,
		'show_continue_to_coding': not coding_completed,
	}
	return render(request, 'interview/aptitude_result.html', context)


@login_required
def coding_round_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

	if not StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.APTITUDE,
		is_completed=True,
	).exists():
		messages.warning(request, 'Complete Stage 1 (Aptitude) first.')
		return redirect('interview:aptitude_round', session_id=session.id)

	if StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.CODING,
		is_completed=True,
	).exists():
		messages.info(request, 'Coding round is locked because it is already completed.')
		return redirect('interview:session_progress', session_id=session.id)

	_ensure_coding_questions_for_session(session)
	deadline_key = f'coding_deadline_{session.id}'

	deadline_timestamp = request.session.get(deadline_key)
	if not deadline_timestamp:
		deadline_timestamp = int((timezone.now() + timedelta(minutes=CODING_DURATION_MINUTES)).timestamp())
		request.session[deadline_key] = deadline_timestamp

	coding_session_questions = CodingSessionQuestion.objects.filter(session=session).select_related('question')
	responses = CodingResponse.objects.filter(session_question__session=session).select_related('session_question')
	responses_map = {response.session_question_id: response for response in responses}
	response_rows = [
		{
			'session_question': item,
			'response': responses_map.get(item.id),
			'visible_case': _extract_visible_sample_case(item.question.test_cases),
		}
		for item in coding_session_questions
	]

	if not coding_session_questions.exists():
		messages.warning(request, 'No coding questions available. Run: python manage.py seed_coding_questions')
		return redirect('interview:dashboard')

	now_timestamp = int(timezone.now().timestamp())
	remaining_seconds = max(0, int(deadline_timestamp) - now_timestamp)

	if remaining_seconds <= 0:
		post_data = request.POST if request.method == 'POST' else {}
		score = _finalize_coding_round(session, coding_session_questions, post_data)
		request.session.pop(deadline_key, None)
		messages.warning(request, f'Time is over. Coding round auto-submitted with score {score}%.')
		return redirect('interview:coding_result', session_id=session.id)

	if request.method == 'POST':
		action = request.POST.get('action', 'submit_round')
		if action.startswith('run_'):
			target_session_question_id = action.replace('run_', '')
			try:
				target_session_question_id = int(target_session_question_id)
			except (TypeError, ValueError):
				messages.error(request, 'Invalid run request.')
				return redirect('interview:coding_round', session_id=session.id)

			target_session_question = get_object_or_404(
				CodingSessionQuestion,
				id=target_session_question_id,
				session=session,
			)
			submitted_code = request.POST.get(f'code_{target_session_question.id}', '').strip()
			language = request.POST.get(
				f'language_{target_session_question.id}',
				CodingResponse.ProgrammingLanguage.PYTHON,
			)
			if language not in dict(CodingResponse.ProgrammingLanguage.choices):
				language = CodingResponse.ProgrammingLanguage.PYTHON

			runner_result = run_code(language, submitted_code)
			response_obj, _ = CodingResponse.objects.get_or_create(session_question=target_session_question)
			response_obj.language = language
			response_obj.submitted_code = submitted_code
			response_obj.run_status = (
				CodingResponse.RunStatus.SUCCESS
				if runner_result['status'] == 'SUCCESS'
				else CodingResponse.RunStatus.ERROR
			)
			response_obj.run_output = runner_result.get('stdout', '')
			response_obj.compile_output = runner_result.get('stderr', '')
			response_obj.save(update_fields=['language', 'submitted_code', 'run_status', 'run_output', 'compile_output'])

			messages.info(
				request,
				f"Run completed via {runner_result.get('engine', 'runner')} for question {target_session_question.display_order}.",
			)
			return redirect('interview:coding_round', session_id=session.id)

		score = _finalize_coding_round(session, coding_session_questions, request.POST)
		request.session.pop(deadline_key, None)
		messages.success(
			request,
			f'Coding round submitted. Stage score: {score}%. Placeholder evaluator used.',
		)
		return redirect('interview:coding_result', session_id=session.id)

	return render(
		request,
		'interview/coding_round.html',
		{
			'session': session,
			'coding_session_questions': coding_session_questions,
			'response_rows': response_rows,
			'language_choices': CodingResponse.ProgrammingLanguage.choices,
			'remaining_seconds': remaining_seconds,
			'coding_duration_minutes': CODING_DURATION_MINUTES,
		},
	)


@login_required
def coding_result_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	stage_result = get_object_or_404(
		StageResult,
		session=session,
		stage_name=StageResult.StageName.CODING,
	)
	responses = CodingResponse.objects.filter(session_question__session=session).select_related('session_question__question')
	technical_completed = StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.TECHNICAL,
		is_completed=True,
	).exists()
	context = {
		'session': session,
		'stage_result': stage_result,
		'responses': responses,
		'show_continue_to_technical': not technical_completed,
	}
	return render(request, 'interview/coding_result.html', context)


@login_required
def technical_round_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

	if not StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.CODING,
		is_completed=True,
	).exists():
		messages.warning(request, 'Complete Stage 2 (Coding) first.')
		return redirect('interview:coding_round', session_id=session.id)

	if StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.TECHNICAL,
		is_completed=True,
	).exists():
		messages.info(request, 'Technical round is locked because it is already completed.')
		return redirect('interview:session_progress', session_id=session.id)

	technical_response, _ = TechnicalResponse.objects.get_or_create(session=session)
	deadline_key = f'technical_deadline_{session.id}'
	deadline_timestamp = request.session.get(deadline_key)
	if not deadline_timestamp:
		deadline_timestamp = int((timezone.now() + timedelta(minutes=TECHNICAL_DURATION_MINUTES)).timestamp())
		request.session[deadline_key] = deadline_timestamp

	now_timestamp = int(timezone.now().timestamp())
	remaining_seconds = max(0, int(deadline_timestamp) - now_timestamp)

	if remaining_seconds <= 0:
		score = _finalize_technical_round(session, technical_response, technical_response.transcript)
		request.session.pop(deadline_key, None)
		messages.warning(request, f'Time is over. Technical round auto-submitted with score {score}%.')
		return redirect('interview:technical_result', session_id=session.id)

	if request.method == 'POST':
		action = request.POST.get('action', 'submit_technical')
		current_transcript = request.POST.get('transcript', '').strip()
		interviewer_notes = request.POST.get('interviewer_notes', '').strip()
		camera_enabled = request.POST.get('camera_enabled') == 'true'
		target_role = request.POST.get('target_role', technical_response.target_role)
		valid_roles = dict(TechnicalResponse.RoleTrack.choices)
		if target_role not in valid_roles:
			target_role = TechnicalResponse.RoleTrack.PYTHON
		read_only_media = _is_serverless_read_only_media()
		technical_response.target_role = target_role
		login_resume_text = (request.session.get('login_resume_text') or '').strip()
		base_resume_text = (technical_response.resume_text or '').strip() or login_resume_text

		previous_role_questions = []
		past_question_sets = TechnicalResponse.objects.filter(
			session__user=session.user,
			target_role=target_role,
		).exclude(
			session=session,
		).values_list('generated_questions', flat=True)
		for question_set in past_question_sets:
			if isinstance(question_set, list):
				for question in question_set:
					if isinstance(question, str) and question.strip():
						previous_role_questions.append(question.strip())

		if action == 'generate_questions':
			resume_text = base_resume_text

			if resume_text:
				match_payload = extract_resume_role_match(resume_text)
				best_match_role = match_payload.get('best_role', technical_response.target_role)
				if technical_response.target_role not in dict(TechnicalResponse.RoleTrack.choices):
					technical_response.target_role = best_match_role

				technical_response.resume_text = resume_text
				technical_response.generated_questions = generate_role_based_questions(
					resume_text,
					target_role=technical_response.target_role,
					exclude_questions=previous_role_questions,
					question_count=20,
				)
				technical_response.interviewer_notes = interviewer_notes
				technical_response.camera_enabled = camera_enabled
				technical_response.save()

				if technical_response.generated_questions:
					messages.success(request, 'Role-based technical questions generated from login resume.')
				else:
					messages.warning(request, 'Resume found but not enough content to generate questions.')
			else:
				messages.warning(request, 'Login resume not found. Please login again and upload resume to generate questions.')

			return redirect('interview:technical_round', session_id=session.id)

		if action == 'transcribe_audio':
			audio_file = request.FILES.get('audio_clip')
			technical_response.transcript = current_transcript
			technical_response.interviewer_notes = interviewer_notes
			technical_response.stt_engine = 'browser'
			technical_response.camera_enabled = camera_enabled
			if audio_file and not read_only_media:
				technical_response.audio_clip = audio_file
			technical_response.save()
			messages.success(request, 'Transcript saved using browser voice input.')
			return redirect('interview:technical_round', session_id=session.id)

		technical_response.transcript = current_transcript
		technical_response.interviewer_notes = interviewer_notes
		technical_response.camera_enabled = camera_enabled
		if base_resume_text and not technical_response.resume_text:
			technical_response.resume_text = base_resume_text
		if technical_response.resume_text and not technical_response.generated_questions:
			technical_response.generated_questions = generate_role_based_questions(
				technical_response.resume_text,
				target_role=technical_response.target_role,
				exclude_questions=previous_role_questions,
				question_count=20,
			)

		if not technical_response.generated_questions:
			messages.warning(request, 'Generate resume-based questions first, then submit technical round.')
			technical_response.save()
			return redirect('interview:technical_round', session_id=session.id)

		technical_response.save()
		score = _finalize_technical_round(session, technical_response, current_transcript)
		request.session.pop(deadline_key, None)

		messages.success(request, f'Technical round submitted. Stage score: {score}%.')
		return redirect('interview:technical_result', session_id=session.id)

	return render(
		request,
		'interview/technical_round.html',
		{
			'session': session,
			'technical_response': technical_response,
			'role_choices': TechnicalResponse.RoleTrack.choices,
			'generated_questions': technical_response.generated_questions,
			'remaining_seconds': remaining_seconds,
			'technical_duration_minutes': TECHNICAL_DURATION_MINUTES,
		},
	)


@login_required
def technical_result_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	stage_result = get_object_or_404(
		StageResult,
		session=session,
		stage_name=StageResult.StageName.TECHNICAL,
	)
	technical_response = TechnicalResponse.objects.filter(session=session).first()
	context = {
		'session': session,
		'stage_result': stage_result,
		'technical_response': technical_response,
	}
	return render(request, 'interview/technical_result.html', context)


@login_required
def hr_round_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

	if not StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.TECHNICAL,
		is_completed=True,
	).exists():
		messages.warning(request, 'Complete Stage 3 (Technical) first.')
		return redirect('interview:technical_round', session_id=session.id)

	if StageResult.objects.filter(
		session=session,
		stage_name=StageResult.StageName.HR,
		is_completed=True,
	).exists():
		messages.info(request, 'HR round is locked because it is already completed.')
		return redirect('interview:session_progress', session_id=session.id)

	hr_response, _ = HRResponse.objects.get_or_create(session=session)

	if request.method == 'POST':
		answers = {}
		for index, _question in enumerate(HR_QUESTIONS, start=1):
			answers[str(index)] = request.POST.get(f'answer_{index}', '').strip()

		score, attempted, summary = _evaluate_hr_answers(answers)
		hr_response.answers = answers
		hr_response.summary = summary
		hr_response.save(update_fields=['answers', 'summary', 'updated_at'])

		StageResult.objects.update_or_create(
			session=session,
			stage_name=StageResult.StageName.HR,
			defaults={
				'score': score,
				'max_score': 100,
				'feedback': summary,
				'is_completed': True,
			},
		)

		session.overall_feedback = summary
		session.status = InterviewSession.SessionStatus.COMPLETED
		session.completed_at = timezone.now()
		session.save(update_fields=['overall_feedback', 'status', 'completed_at'])
		_recalculate_session_weighted_score(session)

		messages.success(request, f'HR round submitted. You answered {attempted} questions. Session completed.')
		return redirect('interview:hr_result', session_id=session.id)

	answer_rows = []
	for index, question in enumerate(HR_QUESTIONS, start=1):
		answer_rows.append(
			{
				'index': index,
				'question': question,
				'answer': (hr_response.answers or {}).get(str(index), ''),
			}
		)

	return render(
		request,
		'interview/hr_round.html',
		{
			'session': session,
			'answer_rows': answer_rows,
			'total_questions': len(HR_QUESTIONS),
		},
	)


@login_required
def hr_result_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	stage_result = get_object_or_404(
		StageResult,
		session=session,
		stage_name=StageResult.StageName.HR,
	)
	hr_response = HRResponse.objects.filter(session=session).first()

	answer_rows = []
	answers = hr_response.answers if hr_response else {}
	for index, question in enumerate(HR_QUESTIONS, start=1):
		answer_rows.append(
			{
				'index': index,
				'question': question,
				'answer': answers.get(str(index), ''),
			}
		)

	return render(
		request,
		'interview/hr_result.html',
		{
			'session': session,
			'stage_result': stage_result,
			'hr_response': hr_response,
			'answer_rows': answer_rows,
		},
	)


@login_required
def overall_result_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	context = {
		'session': session,
		**_build_overall_result_context(session),
	}
	return render(request, 'interview/overall_result.html', context)


@login_required
def download_report_pdf_view(request, session_id):
	session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
	overall_context = _build_overall_result_context(session)
	pdf_file = build_session_report_pdf(session, overall_context)
	filename = f'session_{session.id}_overall_report.pdf'
	pdf_content = pdf_file.read()
	response = HttpResponse(pdf_content, content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="{filename}"'
	response['Content-Length'] = str(len(pdf_content))
	return response
