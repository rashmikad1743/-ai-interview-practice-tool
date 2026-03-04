from django.urls import path

from .views import (
    aptitude_result_view,
    aptitude_round_view,
    coding_result_view,
    coding_round_view,
    dashboard_view,
    download_report_pdf_view,
    hr_result_view,
    hr_round_view,
    overall_result_view,
    reports_view,
    resume_interview_view,
    session_progress_view,
    start_interview_view,
    technical_result_view,
    technical_round_view,
)

app_name = 'interview'

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('start/', start_interview_view, name='start_interview'),
    path('resume/<int:session_id>/', resume_interview_view, name='resume_interview'),
    path('session/<int:session_id>/progress/', session_progress_view, name='session_progress'),
    path('reports/', reports_view, name='reports'),
    path('session/<int:session_id>/aptitude/', aptitude_round_view, name='aptitude_round'),
    path('session/<int:session_id>/aptitude/result/', aptitude_result_view, name='aptitude_result'),
    path('session/<int:session_id>/coding/', coding_round_view, name='coding_round'),
    path('session/<int:session_id>/coding/result/', coding_result_view, name='coding_result'),
    path('session/<int:session_id>/technical/', technical_round_view, name='technical_round'),
    path('session/<int:session_id>/technical/result/', technical_result_view, name='technical_result'),
    path('session/<int:session_id>/hr/', hr_round_view, name='hr_round'),
    path('session/<int:session_id>/hr/result/', hr_result_view, name='hr_result'),
    path('session/<int:session_id>/overall/result/', overall_result_view, name='overall_result'),
    path('session/<int:session_id>/overall/report/pdf/', download_report_pdf_view, name='download_report_pdf'),
]
