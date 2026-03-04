from django.contrib import admin

from .models import (
	AptitudeQuestion,
	AptitudeResponse,
	AptitudeSessionQuestion,
	CodingQuestion,
	CodingResponse,
	CodingSessionQuestion,
	InterviewSession,
	HRResponse,
	StageResult,
	TechnicalResponse,
)


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'status', 'weighted_score', 'started_at', 'completed_at')
	list_filter = ('status', 'started_at')
	search_fields = ('user__username', 'user__email', 'title')


@admin.register(StageResult)
class StageResultAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'stage_name', 'score', 'max_score', 'is_completed', 'submitted_at')
	list_filter = ('stage_name', 'is_completed')
	search_fields = ('session__user__username', 'session__user__email')


@admin.register(AptitudeQuestion)
class AptitudeQuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'topic', 'correct_option', 'is_active', 'created_at')
	list_filter = ('topic', 'is_active')
	search_fields = ('question_text',)


@admin.register(AptitudeSessionQuestion)
class AptitudeSessionQuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'question', 'display_order')
	list_filter = ('session',)
	search_fields = ('session__id', 'question__question_text')


@admin.register(AptitudeResponse)
class AptitudeResponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'session_question', 'selected_option', 'is_correct', 'answered_at')
	list_filter = ('selected_option', 'is_correct')
	search_fields = ('session_question__session__id', 'session_question__question__question_text')


@admin.register(CodingQuestion)
class CodingQuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'difficulty', 'is_active', 'created_at')
	list_filter = ('difficulty', 'is_active')
	search_fields = ('title', 'question_text')


@admin.register(CodingSessionQuestion)
class CodingSessionQuestionAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'question', 'display_order')
	list_filter = ('session',)
	search_fields = ('session__id', 'question__title')


@admin.register(CodingResponse)
class CodingResponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'session_question', 'score', 'submitted_at')
	list_filter = ('score',)
	search_fields = ('session_question__session__id', 'session_question__question__title')


@admin.register(TechnicalResponse)
class TechnicalResponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'stt_engine', 'camera_enabled', 'updated_at')
	list_filter = ('stt_engine', 'camera_enabled')
	search_fields = ('session__id', 'transcript')


@admin.register(HRResponse)
class HRResponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'session', 'updated_at')
	search_fields = ('session__id', 'summary')
