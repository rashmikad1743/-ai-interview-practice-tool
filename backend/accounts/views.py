from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from interview.services.resume_ai import extract_resume_text, extract_resume_role_match

from .forms import ResumeLoginForm, SignUpForm


def landing_view(request):
	if request.user.is_authenticated:
		return redirect('interview:dashboard')
	return render(request, 'accounts/landing.html')


def signup_view(request):
	if request.user.is_authenticated:
		return redirect('interview:dashboard')

	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, 'Account created successfully.')
			return redirect('interview:dashboard')
	else:
		form = SignUpForm()

	return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('interview:dashboard')

	if request.method == 'POST':
		form = ResumeLoginForm(request=request, data=request.POST, files=request.FILES)
		if form.is_valid():
			user = form.get_user()
			resume_file = form.cleaned_data.get('resume_file')
			resume_text = extract_resume_text(resume_file)

			if not resume_text.strip():
				messages.error(request, 'Resume text could not be extracted. Upload a text-based PDF/TXT resume.')
				return render(request, 'accounts/login.html', {'form': form})

			match_payload = extract_resume_role_match(resume_text)
			request.session['login_resume_text'] = resume_text
			request.session['login_resume_keywords'] = match_payload.get('keywords', [])
			request.session['login_role_scores'] = match_payload.get('role_scores', {})
			request.session['login_best_role'] = match_payload.get('best_role', 'PYTHON')

			login(request, user)
			messages.success(request, 'Login successful. Resume analyzed and technical questions are being prepared in background.')
			return redirect('interview:dashboard')
	else:
		form = ResumeLoginForm(request=request)

	return render(request, 'accounts/login.html', {'form': form})


@login_required
def home_redirect(request):
	return redirect('interview:dashboard')
