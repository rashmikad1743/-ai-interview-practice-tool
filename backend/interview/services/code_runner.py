import json
import os
import urllib.error
import urllib.request
import ast
import subprocess
import tempfile
import sys


JUDGE0_LANGUAGE_ID_MAP = {
    'PYTHON': 71,
    'JAVA': 62,
    'CPP': 54,
    'JS': 63,
}


def _run_with_placeholder(language, submitted_code):
    code = (submitted_code or '').strip()
    if not code:
        return {
            'status': 'ERROR',
            'stdout': '',
            'stderr': 'No code submitted.',
            'engine': 'placeholder',
        }

    language_labels = {
        'PYTHON': 'Python',
        'JAVA': 'Java',
        'CPP': 'C++',
        'JS': 'JavaScript',
    }
    label = language_labels.get(language, language)

    if 'print(' in code or 'console.log' in code or 'System.out.println' in code or 'cout <<' in code:
        output = f'[{label}] Placeholder run successful. Print statement detected.'
    else:
        output = f'[{label}] Code received. Placeholder runner does not execute code yet.'

    return {
        'status': 'SUCCESS',
        'stdout': output,
        'stderr': '',
        'engine': 'placeholder',
    }


def _run_with_judge0(language, submitted_code):
    judge0_base = os.getenv('JUDGE0_API_URL', '').strip()
    judge0_api_key = os.getenv('JUDGE0_API_KEY', '').strip()
    if not judge0_base:
        return None

    language_id = JUDGE0_LANGUAGE_ID_MAP.get(language)
    if not language_id:
        return {
            'status': 'ERROR',
            'stdout': '',
            'stderr': f'Unsupported language for Judge0: {language}',
            'engine': 'judge0',
        }

    submit_url = judge0_base.rstrip('/') + '/submissions?base64_encoded=false&wait=true'
    payload = {
        'language_id': language_id,
        'source_code': submitted_code,
        'stdin': '',
    }
    encoded_payload = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
    }
    if judge0_api_key:
        headers['X-Auth-Token'] = judge0_api_key

    req = urllib.request.Request(submit_url, data=encoded_payload, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read().decode('utf-8')
            result = json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='ignore')
        return {
            'status': 'ERROR',
            'stdout': '',
            'stderr': f'Judge0 HTTP error: {exc.code}. {body}',
            'engine': 'judge0',
        }
    except Exception as exc:
        return {
            'status': 'ERROR',
            'stdout': '',
            'stderr': f'Judge0 request failed: {exc}',
            'engine': 'judge0',
        }

    status_description = (result.get('status') or {}).get('description', '')
    stderr = result.get('stderr') or ''
    compile_output = result.get('compile_output') or ''
    stdout = result.get('stdout') or ''

    final_stderr = '\n'.join(part for part in [stderr, compile_output] if part).strip()
    status = 'SUCCESS' if not final_stderr and status_description.lower() == 'accepted' else 'ERROR'

    return {
        'status': status,
        'stdout': stdout,
        'stderr': final_stderr or status_description,
        'engine': 'judge0',
    }


def run_code(language, submitted_code):
    judge0_result = _run_with_judge0(language, submitted_code)
    if judge0_result is not None:
        return judge0_result
    return _run_with_placeholder(language, submitted_code)


def _keyword_score(submitted_code, expected_keywords):
    code = (submitted_code or '').strip().lower()
    if not code:
        return 0.0, 'No code submitted.'

    keywords = [item.strip().lower() for item in (expected_keywords or '').split(',') if item.strip()]
    if not keywords:
        return 50.0, 'Code captured. No test-cases configured, default baseline score used.'

    matched = sum(1 for keyword in keywords if keyword in code)
    score = round((matched / len(keywords)) * 100, 2)
    return score, f'Keyword fallback score: matched {matched}/{len(keywords)} expected keywords.'


def _extract_function_names(source_code):
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return None

    names = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            names.append(node.name)
    return names


def _outputs_equal(actual, expected):
    if isinstance(actual, float) or isinstance(expected, float):
        try:
            return abs(float(actual) - float(expected)) < 1e-9
        except Exception:
            return str(actual).strip() == str(expected).strip()

    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        if len(actual) != len(expected):
            return False
        return all(_outputs_equal(a, e) for a, e in zip(actual, expected))

    if isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual.keys()) != set(expected.keys()):
            return False
        return all(_outputs_equal(actual[key], expected[key]) for key in actual.keys())

    return str(actual).strip() == str(expected).strip()


def _build_testcase_feedback(results):
    visible_cases = [item for item in results if item.get('is_visible')]
    hidden_cases = [item for item in results if not item.get('is_visible')]

    visible_pass = any(item.get('ok') for item in visible_cases) if visible_cases else False
    hidden_passed = sum(1 for item in hidden_cases if item.get('ok'))
    hidden_total = len(hidden_cases)

    passed = sum(1 for item in results if item.get('ok'))
    total = len(results)

    lines = [
        f"Visible Test Case: {'Passed' if visible_pass else 'Failed'}",
        f"Hidden Test Cases: {hidden_passed}/{hidden_total} Passed",
        f'Final Score: {passed}/{total}',
    ]

    first_failure = next((item for item in results if not item.get('ok')), None)
    if first_failure:
        reason = first_failure.get('error') or f"expected={first_failure.get('expected')}, got={first_failure.get('actual')}"
        lines.append(f'Error: {reason}')

    return '\n'.join(lines), passed, total


def _normalize_test_cases(test_cases):
    normalized = []
    for index, case in enumerate(test_cases or []):
        if not isinstance(case, dict):
            continue

        raw_input = case.get('input')
        if isinstance(raw_input, list):
            list_input = raw_input
        elif isinstance(raw_input, tuple):
            list_input = list(raw_input)
        elif isinstance(raw_input, dict) and '__args__' in raw_input:
            unpacked = raw_input.get('__args__', [])
            if isinstance(unpacked, list):
                list_input = unpacked
            elif isinstance(unpacked, tuple):
                list_input = list(unpacked)
            else:
                list_input = [unpacked]
        else:
            list_input = [raw_input]

        normalized.append(
            {
                'is_visible': bool(case.get('visible', index == 0)),
                'input': list_input,
                'expected': case.get('expected'),
                'function_name': case.get('function_name'),
            }
        )
    return normalized


def _evaluate_python_test_cases(submitted_code, test_cases):
    code_text = (submitted_code or '').strip()
    if not code_text:
        return 0.0, 'No code submitted.'

    try:
        ast.parse(code_text)
    except SyntaxError as exc:
        return 0.0, f'Syntax error: {exc}'

    cases = _normalize_test_cases(test_cases)
    if not cases:
        return 0.0, 'No test cases configured for this question.'

    function_names = _extract_function_names(code_text)
    if function_names is None:
        return 0.0, 'Syntax error while parsing submitted code.'
    if not function_names:
        return 0.0, 'Incorrect function name: no function found. Define expected function and submit again.'

    expected_function_name = next((item.get('function_name') for item in cases if item.get('function_name')), None)
    if expected_function_name and expected_function_name not in function_names:
        return 0.0, f"Incorrect function name: expected '{expected_function_name}'."

    function_name = expected_function_name or function_names[0]

    encoded_cases = json.dumps(cases)

    script = f"""
import json

{code_text}

cases = json.loads({json.dumps(encoded_cases)})
results = []
target = {function_name}

for idx, case in enumerate(cases):
    raw_input = case.get('input')
    expected = case.get('expected')
    is_visible = bool(case.get('is_visible', idx == 0))
    try:
        actual = target(raw_input)

        results.append({{
            'ok': True,
            'actual': actual,
            'expected': expected,
            'is_visible': is_visible,
            'error': ''
        }})
    except TypeError as exc:
        results.append({{
            'ok': False,
            'actual': None,
            'expected': expected,
            'is_visible': is_visible,
            'error': f'Incorrect arguments: {{exc}}'
        }})
    except Exception as exc:
        results.append({{
            'ok': False,
            'actual': None,
            'expected': expected,
            'is_visible': is_visible,
            'error': f'Runtime error: {{exc}}'
        }})

print(json.dumps(results))
"""

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(script)
            temp_path = temp_file.name

        process = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 0.0, 'Execution timed out while running test cases.'
    except Exception as exc:
        return 0.0, f'Execution failed: {exc}'
    finally:
        try:
            if temp_path:
                os.remove(temp_path)
        except Exception:
            pass

    if process.returncode != 0:
        stderr = (process.stderr or '').strip()
        return 0.0, f'Code execution error: {stderr or "Unknown runtime error"}'

    try:
        parsed = json.loads((process.stdout or '').strip().splitlines()[-1])
    except Exception:
        return 0.0, 'Could not parse test-case output from submitted code.'

    for item in parsed:
        if item.get('ok'):
            item['ok'] = _outputs_equal(item.get('actual'), item.get('expected'))

    total = len(parsed)
    passed = sum(1 for item in parsed if item.get('ok'))
    score = round((passed / total) * 100, 2) if total else 0.0

    feedback, _, _ = _build_testcase_feedback(parsed)

    return score, feedback


def evaluate_coding_submission(language, submitted_code, test_cases=None, expected_keywords=''):
    if language == 'PYTHON' and test_cases:
        return _evaluate_python_test_cases(submitted_code, test_cases)

    return _keyword_score(submitted_code, expected_keywords)
