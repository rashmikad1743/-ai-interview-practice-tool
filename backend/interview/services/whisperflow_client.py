import os
from typing import Optional


def transcribe_with_whisperflow(audio_file, fallback_transcript: str = ''):
    """
    WhisperFlow-ready adapter.
    - If WHISPERFLOW_API_URL is configured and requests is available, sends audio to API.
    - Otherwise returns fallback transcript from browser speech recognition.
    """

    api_url = os.getenv('WHISPERFLOW_API_URL', '').strip()
    api_key = os.getenv('WHISPERFLOW_API_KEY', '').strip()

    if not audio_file:
        return {
            'ok': False,
            'engine': 'none',
            'text': fallback_transcript or '',
            'error': 'No audio file provided.',
        }

    if not api_url:
        return {
            'ok': True,
            'engine': 'browser',
            'text': fallback_transcript or '',
            'error': '',
        }

    try:
        import requests
    except Exception:
        return {
            'ok': True,
            'engine': 'browser',
            'text': fallback_transcript or '',
            'error': 'requests package not installed; using browser transcript fallback.',
        }

    files = {
        'file': (audio_file.name, audio_file.read(), getattr(audio_file, 'content_type', 'audio/webm')),
    }
    data = {
        'task': 'transcribe',
    }
    headers = {}
    if api_key:
        headers['Authorization'] = f'Bearer {api_key}'

    try:
        response = requests.post(api_url, files=files, data=data, headers=headers, timeout=40)
        response.raise_for_status()
        payload = response.json() if response.content else {}

        text = (
            payload.get('text')
            or payload.get('transcript')
            or payload.get('result')
            or fallback_transcript
            or ''
        )

        return {
            'ok': True,
            'engine': 'whisperflow',
            'text': text,
            'error': '',
        }
    except Exception as exc:
        return {
            'ok': True,
            'engine': 'browser',
            'text': fallback_transcript or '',
            'error': f'WhisperFlow request failed: {exc}. Using browser transcript fallback.',
        }
