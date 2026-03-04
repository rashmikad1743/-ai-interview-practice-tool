from django.conf import settings
from django.db import models


class InterviewSession(models.Model):
	class SessionStatus(models.TextChoices):
		IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
		COMPLETED = 'COMPLETED', 'Completed'

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='interview_sessions',
	)
	title = models.CharField(max_length=200, blank=True)
	status = models.CharField(
		max_length=20,
		choices=SessionStatus.choices,
		default=SessionStatus.IN_PROGRESS,
	)
	weighted_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
	overall_feedback = models.TextField(blank=True)
	report_pdf = models.FileField(upload_to='reports/', null=True, blank=True)
	started_at = models.DateTimeField(auto_now_add=True)
	completed_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-started_at']

	def __str__(self):
		return f"Session #{self.id} - {self.user.username}"


class StageResult(models.Model):
	class StageName(models.TextChoices):
		APTITUDE = 'APTITUDE', 'Aptitude'
		CODING = 'CODING', 'Coding'
		TECHNICAL = 'TECHNICAL', 'Technical'
		HR = 'HR', 'HR'

	session = models.ForeignKey(
		InterviewSession,
		on_delete=models.CASCADE,
		related_name='stage_results',
	)
	stage_name = models.CharField(max_length=20, choices=StageName.choices)
	score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
	feedback = models.TextField(blank=True)
	is_completed = models.BooleanField(default=False)
	submitted_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['id']
		constraints = [
			models.UniqueConstraint(
				fields=['session', 'stage_name'],
				name='unique_stage_result_per_session',
			)
		]

	def __str__(self):
		return f"{self.session_id} - {self.stage_name}"


class AptitudeQuestion(models.Model):
	class CorrectOption(models.TextChoices):
		A = 'A', 'Option A'
		B = 'B', 'Option B'
		C = 'C', 'Option C'
		D = 'D', 'Option D'

	question_text = models.TextField()
	topic = models.CharField(max_length=120, blank=True)
	option_a = models.CharField(max_length=255)
	option_b = models.CharField(max_length=255)
	option_c = models.CharField(max_length=255)
	option_d = models.CharField(max_length=255)
	correct_option = models.CharField(max_length=1, choices=CorrectOption.choices)
	explanation = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['id']

	def __str__(self):
		return f"Q{self.id} - {self.topic or 'General'}"


class AptitudeSessionQuestion(models.Model):
	session = models.ForeignKey(
		InterviewSession,
		on_delete=models.CASCADE,
		related_name='aptitude_questions',
	)
	question = models.ForeignKey(
		AptitudeQuestion,
		on_delete=models.CASCADE,
		related_name='session_mappings',
	)
	display_order = models.PositiveIntegerField()

	class Meta:
		ordering = ['display_order']
		constraints = [
			models.UniqueConstraint(
				fields=['session', 'question'],
				name='unique_aptitude_question_per_session',
			),
			models.UniqueConstraint(
				fields=['session', 'display_order'],
				name='unique_aptitude_order_per_session',
			),
		]

	def __str__(self):
		return f"Session {self.session_id} - Q{self.question_id}"


class AptitudeResponse(models.Model):
	class SelectedOption(models.TextChoices):
		A = 'A', 'Option A'
		B = 'B', 'Option B'
		C = 'C', 'Option C'
		D = 'D', 'Option D'

	session_question = models.OneToOneField(
		AptitudeSessionQuestion,
		on_delete=models.CASCADE,
		related_name='response',
	)
	selected_option = models.CharField(max_length=1, choices=SelectedOption.choices)
	is_correct = models.BooleanField(default=False)
	answered_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['session_question__display_order']

	def __str__(self):
		return f"SessionQ {self.session_question_id} - {self.selected_option}"


class CodingQuestion(models.Model):
	class Difficulty(models.TextChoices):
		EASY = 'EASY', 'Easy'
		MEDIUM = 'MEDIUM', 'Medium'

	title = models.CharField(max_length=180)
	question_text = models.TextField()
	difficulty = models.CharField(max_length=10, choices=Difficulty.choices)
	expected_keywords = models.CharField(
		max_length=255,
		help_text='Comma separated words used by placeholder evaluator.',
		blank=True,
	)
	test_cases = models.JSONField(default=list, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['id']

	def __str__(self):
		return f"{self.title} ({self.difficulty})"


class CodingSessionQuestion(models.Model):
	session = models.ForeignKey(
		InterviewSession,
		on_delete=models.CASCADE,
		related_name='coding_questions',
	)
	question = models.ForeignKey(
		CodingQuestion,
		on_delete=models.CASCADE,
		related_name='session_mappings',
	)
	display_order = models.PositiveIntegerField()

	class Meta:
		ordering = ['display_order']
		constraints = [
			models.UniqueConstraint(
				fields=['session', 'question'],
				name='unique_coding_question_per_session',
			),
			models.UniqueConstraint(
				fields=['session', 'display_order'],
				name='unique_coding_order_per_session',
			),
		]

	def __str__(self):
		return f"Session {self.session_id} - CodingQ {self.question_id}"


class CodingResponse(models.Model):
	class ProgrammingLanguage(models.TextChoices):
		PYTHON = 'PYTHON', 'Python'
		JAVA = 'JAVA', 'Java'
		CPP = 'CPP', 'C++'
		JS = 'JS', 'JavaScript'

	class RunStatus(models.TextChoices):
		NOT_RUN = 'NOT_RUN', 'Not Run'
		SUCCESS = 'SUCCESS', 'Success'
		ERROR = 'ERROR', 'Error'

	session_question = models.OneToOneField(
		CodingSessionQuestion,
		on_delete=models.CASCADE,
		related_name='response',
	)
	language = models.CharField(
		max_length=10,
		choices=ProgrammingLanguage.choices,
		default=ProgrammingLanguage.PYTHON,
	)
	submitted_code = models.TextField(blank=True)
	run_status = models.CharField(
		max_length=12,
		choices=RunStatus.choices,
		default=RunStatus.NOT_RUN,
	)
	run_output = models.TextField(blank=True)
	compile_output = models.TextField(blank=True)
	score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	feedback = models.TextField(blank=True)
	submitted_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['session_question__display_order']

	def __str__(self):
		return f"CodingResponse {self.session_question_id}"


class TechnicalResponse(models.Model):
	class RoleTrack(models.TextChoices):
		AIML = 'AIML', 'AIML Engineer'
		WEB_DEV = 'WEB_DEV', 'Web Development'
		UI_UX = 'UI_UX', 'UI/UX Designer'
		FRONTEND = 'FRONTEND', 'Frontend Developer (HTML/CSS/JS/React)'
		BACKEND = 'BACKEND', 'Backend Developer'
		FULL_STACK = 'FULL_STACK', 'Full Stack Developer'
		MERN_STACK = 'MERN_STACK', 'MERN Stack Developer'
		DEVOPS = 'DEVOPS', 'DevOps Engineer'
		DATA_ANALYST = 'DATA_ANALYST', 'Data Analyst'
		DATA_SCIENTIST = 'DATA_SCIENTIST', 'Data Scientist'
		QA_AUTOMATION = 'QA_AUTOMATION', 'QA Automation Engineer'
		CYBERSECURITY = 'CYBERSECURITY', 'Cybersecurity Analyst'
		CLOUD_ENGINEER = 'CLOUD_ENGINEER', 'Cloud Engineer'
		ANDROID = 'ANDROID', 'Android Developer'
		IOS = 'IOS', 'iOS Developer'
		PHP = 'PHP', 'PHP Developer'
		JAVASCRIPT = 'JAVASCRIPT', 'JavaScript Developer'
		PYTHON = 'PYTHON', 'Python Developer'
		GEN_AI = 'GEN_AI', 'Generative AI'
		JAVA = 'JAVA', 'Java Developer'
		ANGULAR = 'ANGULAR', 'Angular Developer'
		DOTNET = 'DOTNET', '.NET Developer'

	session = models.OneToOneField(
		InterviewSession,
		on_delete=models.CASCADE,
		related_name='technical_response',
	)
	target_role = models.CharField(
		max_length=20,
		choices=RoleTrack.choices,
		default=RoleTrack.PYTHON,
	)
	resume_file = models.FileField(upload_to='technical_resume/', null=True, blank=True)
	resume_text = models.TextField(blank=True)
	generated_questions = models.JSONField(default=list, blank=True)
	audio_clip = models.FileField(upload_to='technical_audio/', null=True, blank=True)
	transcript = models.TextField(blank=True)
	interviewer_notes = models.TextField(blank=True)
	stt_engine = models.CharField(max_length=40, default='browser')
	camera_enabled = models.BooleanField(default=False)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-updated_at']

	def __str__(self):
		return f"TechnicalResponse Session {self.session_id}"


class HRResponse(models.Model):
	session = models.OneToOneField(
		InterviewSession,
		on_delete=models.CASCADE,
		related_name='hr_response',
	)
	answers = models.JSONField(default=dict, blank=True)
	summary = models.TextField(blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-updated_at']

	def __str__(self):
		return f"HRResponse Session {self.session_id}"
