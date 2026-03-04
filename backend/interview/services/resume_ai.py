import re
import random
import threading
from pathlib import Path


ROLE_LABELS = {
    'AIML': 'AIML Engineer',
    'WEB_DEV': 'Web Development',
    'UI_UX': 'UI/UX Designer',
    'FRONTEND': 'Frontend Developer (HTML/CSS/JS/React)',
    'BACKEND': 'Backend Developer',
    'FULL_STACK': 'Full Stack Developer',
    'MERN_STACK': 'MERN Stack Developer',
    'DEVOPS': 'DevOps Engineer',
    'DATA_ANALYST': 'Data Analyst',
    'DATA_SCIENTIST': 'Data Scientist',
    'QA_AUTOMATION': 'QA Automation Engineer',
    'CYBERSECURITY': 'Cybersecurity Analyst',
    'CLOUD_ENGINEER': 'Cloud Engineer',
    'ANDROID': 'Android Developer',
    'IOS': 'iOS Developer',
    'PHP': 'PHP Developer',
    'JAVASCRIPT': 'JavaScript Developer',
    'PYTHON': 'Python Developer',
    'GEN_AI': 'Generative AI',
    'JAVA': 'Java Developer',
    'ANGULAR': 'Angular Developer',
    'DOTNET': '.NET Developer',
}

_FLAN_PIPELINE = None
_FLAN_INIT_LOCK = threading.Lock()


ROLE_QUESTION_BANK = {
    'AIML': [
        'What is the difference between supervised, unsupervised, and reinforcement learning?',
        'How do you handle missing values and outliers in ML datasets?',
        'Explain bias-variance trade-off with a practical example.',
        'When would you choose logistic regression vs decision trees?',
        'What evaluation metrics would you use for imbalanced classification?',
        'How do feature scaling and normalization impact model training?',
        'Explain cross-validation strategies and when to use stratified folds.',
        'How do you perform feature selection for high-dimensional data?',
        'How do you diagnose overfitting in deep learning models?',
        'Explain batch normalization and dropout in neural networks.',
        'How do CNNs differ from transformers for vision and NLP tasks?',
        'How do you select hyperparameter tuning strategy: grid, random, or Bayesian optimization?',
        'How would you design an end-to-end MLOps pipeline for model deployment?',
        'How do you monitor model drift and trigger retraining?',
        'How do you design feature stores and version datasets/models reproducibly?',
        'How do you evaluate fairness and mitigate bias in AI systems?',
        'How do you choose between batch inference and real-time inference?',
        'How do you optimize inference latency and throughput under cost constraints?',
        'How do you design experiment tracking and model registry workflows?',
        'How would you design an LLM-powered feature with RAG and safety guardrails?',
    ],
    'WEB_DEV': [
        'Explain the request-response lifecycle of a web application.',
        'Difference between session-based auth and token-based auth.',
        'What are semantic HTML and accessibility best practices?',
        'How do you optimize Core Web Vitals for a production app?',
        'What is CORS and how do you configure it safely?',
        'Explain SQL joins and indexing strategy for web apps.',
        'How would you design REST APIs with proper versioning and pagination?',
        'How do you prevent XSS, CSRF, and SQL injection in production?',
        'What caching layers would you add (browser, CDN, app, DB) and why?',
        'How do you debug and profile slow backend endpoints?',
        'How would you scale a monolithic web app under heavy traffic?',
        'Explain blue-green deployment and rollback strategy.',
    ],
    'UI_UX': [
        'What is the difference between UI and UX in product design?',
        'How do you start a design process for a new feature from scratch?',
        'What is user research and when should it be done?',
        'How do personas and user journeys help in design decisions?',
        'What is information architecture and why is it important?',
        'How do you create effective wireframes before high-fidelity designs?',
        'What are design systems and reusable components?',
        'How do typography, spacing, and color hierarchy improve usability?',
        'What are accessibility basics (contrast, keyboard nav, labels) in UI design?',
        'How do you evaluate if a design is intuitive for first-time users?',
        'What is the purpose of prototypes and when to use low vs high fidelity?',
        'How do you run a simple usability test and collect actionable feedback?',
        'How do you balance business goals with user needs in design?',
        'What are common mobile UX mistakes and how do you avoid them?',
        'How do you design responsive experiences across desktop, tablet, and mobile?',
        'How do you collaborate with developers to ensure design implementation quality?',
        'What metrics can be used to measure UX success after release?',
        'How do you handle conflicting feedback from stakeholders and users?',
        'How do you iterate on an existing design that has low engagement?',
        'Walk through one UI/UX project from your resume and explain your end-to-end design decisions.',
    ],
    'FRONTEND': [
        'Explain semantic HTML and why it matters for accessibility and SEO.',
        'How does the CSS box model work, and how do margin/padding/border interact?',
        'Difference between CSS Grid and Flexbox, and when to use each?',
        'How do you build responsive layouts for mobile-first design?',
        'Explain JavaScript event loop, call stack, and async behavior in browser UIs.',
        'How do you prevent and debug DOM reflow/repaint performance issues?',
        'What are React components, props, and state with a real example?',
        'How do hooks like useEffect and useMemo work, and common pitfalls?',
        'How do you manage state in React for medium to large apps?',
        'How do you optimize React rendering and bundle size in production?',
        'How do you handle authentication, protected routes, and token refresh on frontend?',
        'How do you test frontend apps (unit, integration, end-to-end) and ensure reliability?',
    ],
    'BACKEND': [
        'Explain backend architecture layers: controller, service, repository, and data access.',
        'How do you design RESTful APIs with proper status codes and error contracts?',
        'Difference between SQL and NoSQL and when to choose each?',
        'How do indexing and query planning improve database performance?',
        'How do you implement authentication and authorization securely on server side?',
        'How do you prevent backend vulnerabilities like SQL injection and SSRF?',
        'How do you design idempotent APIs and handle retries safely?',
        'How do caching patterns (Redis, query cache, CDN) reduce latency?',
        'How do you build background processing with queues and workers?',
        'How do you instrument logging, metrics, and tracing for observability?',
        'How do you scale backend systems for high traffic and reliability?',
        'How do you design database migrations and backward-compatible deployments?',
    ],
    'FULL_STACK': [
        'How do frontend and backend interact in a full stack application end-to-end?',
        'How do you design and document API contracts consumed by multiple UIs?',
        'How do you manage shared validation rules across frontend and backend?',
        'How do you implement authentication flow from UI login to backend token/session handling?',
        'How do you model relational data and expose it to frontend efficiently?',
        'How do you handle pagination, filtering, and sorting across stack layers?',
        'How do you optimize perceived performance from browser rendering to API latency?',
        'How do you ensure secure coding across both client and server?',
        'How do you implement CI/CD for a full stack project with rollback strategy?',
        'How do you debug production issues spanning frontend, API, and database?',
        'How do you design scalable architecture for a growing full stack product?',
        'How do you decide monolith vs microservices for full stack teams?',
    ],
    'MERN_STACK': [
        'Explain the full request lifecycle in MERN: React client, Express API, MongoDB storage.',
        'How does MongoDB document modeling differ from relational modeling?',
        'How do Mongoose schemas and validations work in production APIs?',
        'How do you structure Express middleware for auth, validation, and error handling?',
        'How do React hooks and context integrate with API state in MERN apps?',
        'How do you implement JWT auth flow securely in MERN stack?',
        'How do you optimize MongoDB queries with indexes and aggregation pipelines?',
        'How do you handle file uploads and media storage in MERN applications?',
        'How do you implement role-based authorization across React and Express?',
        'How do you optimize performance and bundle size in React + Node deployments?',
        'How do you design scalable folder structure and code separation in MERN projects?',
        'How do you deploy and monitor MERN apps with environment-specific configuration?',
    ],
    'DEVOPS': [
        'What is CI/CD and why is it critical for modern software teams?',
        'How do you design a deployment pipeline with build, test, and release stages?',
        'What is Infrastructure as Code and where would you use Terraform?',
        'How do Docker containers differ from virtual machines?',
        'How do you orchestrate services with Kubernetes in production?',
        'How do you implement blue-green or canary deployments safely?',
        'How do you set up centralized logging and observability for microservices?',
        'How do you monitor system health and define SLO/SLI alerts?',
        'What strategies do you use for secret management and credential rotation?',
        'How do you handle incident response and postmortems in DevOps?',
        'How do you optimize infrastructure cost without reducing reliability?',
        'How do you secure CI/CD pipelines against supply-chain attacks?',
    ],
    'DATA_ANALYST': [
        'How do you clean and validate messy business data before analysis?',
        'How do you choose between descriptive, diagnostic, and predictive analysis?',
        'Explain SQL joins and when each join type is used in reporting.',
        'How do you design dashboards for non-technical stakeholders?',
        'How do you define KPIs aligned with business goals?',
        'How do you detect anomalies and data quality issues in reports?',
        'How do you use Excel/Python/SQL together in analysis workflows?',
        'How do you communicate uncertainty and assumptions in your analysis?',
        'How do you perform cohort or funnel analysis for product metrics?',
        'How do A/B testing results influence business decisions?',
        'How do you prioritize ad-hoc analysis requests from multiple teams?',
        'How do you make analytics reproducible and auditable?',
    ],
    'DATA_SCIENTIST': [
        'How does a data scientist approach problem framing with stakeholders?',
        'How do you perform EDA and feature engineering for noisy datasets?',
        'How do you choose baseline models before complex algorithms?',
        'How do you evaluate classification vs regression model performance?',
        'How do you manage imbalanced data and sampling strategies?',
        'How do you avoid leakage while splitting train/validation/test sets?',
        'How do you tune hyperparameters efficiently in production constraints?',
        'How do you explain model behavior using SHAP/LIME or similar methods?',
        'How do you deploy models and measure post-deployment drift?',
        'How do you run experiment tracking and model versioning workflows?',
        'How do you balance accuracy, interpretability, and latency trade-offs?',
        'How do you collaborate with data engineers and product teams effectively?',
    ],
    'QA_AUTOMATION': [
        'What is the difference between functional, integration, and end-to-end testing?',
        'How do you decide what to automate vs what to keep manual?',
        'How do you structure maintainable UI automation test suites?',
        'How do you use Page Object Model in Selenium/Playwright tests?',
        'How do you test APIs with automated regression pipelines?',
        'How do you design test data management for repeatable test runs?',
        'How do you integrate automation suites into CI pipelines?',
        'How do you reduce flaky tests and improve test stability?',
        'How do you define test coverage metrics that matter?',
        'How do you perform performance and load validation in QA automation?',
        'How do you report defects with strong reproduction evidence?',
        'How do you enforce quality gates before production release?',
    ],
    'CYBERSECURITY': [
        'What are common web vulnerabilities and how do you mitigate them?',
        'How do you perform threat modeling for an application?',
        'How do authentication and authorization differ from a security perspective?',
        'How do you secure APIs against abuse and injection attacks?',
        'What is zero-trust architecture and when is it useful?',
        'How do you manage security logging and incident detection?',
        'How do encryption at rest and in transit differ?',
        'How do you handle vulnerability scanning and patch management?',
        'How do you secure cloud resources using IAM best practices?',
        'What is the role of SOC and SIEM in enterprise security?',
        'How do you respond to a suspected data breach incident?',
        'How do you balance security controls with developer productivity?',
    ],
    'CLOUD_ENGINEER': [
        'How do you design scalable and highly available cloud architecture?',
        'When would you choose IaaS vs PaaS vs serverless services?',
        'How do you manage networking in cloud environments (VPC, subnets, routing)?',
        'How do you implement IAM least-privilege policies in cloud?',
        'How do you design cloud backup, disaster recovery, and failover?',
        'How do you automate cloud provisioning with IaC tools?',
        'How do you optimize cloud cost using right-sizing and autoscaling?',
        'How do you monitor cloud workloads and set meaningful alerts?',
        'How do CDN and caching improve cloud application performance?',
        'How do you secure containerized workloads in the cloud?',
        'How do you choose between managed databases and self-hosted options?',
        'How do you implement multi-environment deployment strategy in cloud?',
    ],
    'ANDROID': [
        'Explain Android activity lifecycle and common pitfalls.',
        'How do you structure Android apps using MVVM architecture?',
        'How do LiveData/StateFlow help in reactive UI updates?',
        'How do you manage dependency injection in Android apps?',
        'How do you handle local storage with Room database?',
        'How do you design resilient API communication on mobile networks?',
        'How do you optimize app startup time and performance?',
        'How do you manage background tasks with WorkManager?',
        'How do you secure Android apps against reverse engineering risks?',
        'How do you implement offline-first behavior in Android apps?',
        'How do you test Android applications effectively?',
        'How do you publish and monitor apps on Play Store?',
    ],
    'IOS': [
        'Explain iOS app lifecycle and view controller responsibilities.',
        'How do you structure Swift applications using MVVM or clean architecture?',
        'How do Swift optionals and error handling improve code safety?',
        'How do you manage asynchronous code with async/await in iOS?',
        'How do you persist data with Core Data or local databases?',
        'How do you design robust networking layers for iOS apps?',
        'How do you optimize app memory usage and performance in iOS?',
        'How do you secure sensitive data in iOS keychain?',
        'How do you support offline mode and sync conflicts in mobile apps?',
        'How do you write UI tests and unit tests for iOS?',
        'How do you integrate analytics and crash monitoring in iOS apps?',
        'How do you manage App Store release and rollback strategy?',
    ],
    'PHP': [
        'Explain PHP request lifecycle and execution model.',
        'What are namespaces and autoloading (Composer) in PHP?',
        'How do you structure a clean MVC PHP application?',
        'Difference between include, require, include_once, require_once.',
        'How do you secure PHP forms and validate user input?',
        'How do you optimize MySQL queries in PHP applications?',
        'How do you manage sessions and authentication securely in PHP?',
        'Explain dependency injection in Laravel/Symfony context.',
        'How do queues and jobs work in a PHP framework?',
        'How do you design testable PHP services with PHPUnit?',
        'How would you scale a PHP app with Redis and workers?',
        'How do you handle zero-downtime deployment in PHP projects?',
    ],
    'JAVASCRIPT': [
        'Explain `var`, `let`, and `const` with scope behavior.',
        'What is event loop and how microtasks differ from macrotasks?',
        'Explain closures with a practical use case.',
        'How does prototypal inheritance work in JavaScript?',
        'Difference between `==` and `===` and common pitfalls.',
        'How do promises, async/await, and error handling work together?',
        'What is debouncing vs throttling and where to use them?',
        'How would you manage state in a large frontend app?',
        'How do you optimize rendering and bundle size in SPA apps?',
        'How would you debug memory leaks in JavaScript applications?',
        'How do you design resilient API integration with retries/backoff?',
        'How do you apply advanced TypeScript typing in JS-heavy projects?',
    ],
    'PYTHON': [
        'Explain Python data types and mutability with examples.',
        'What are list comprehensions and generator expressions?',
        'Difference between shallow and deep copy in Python.',
        'How do decorators work and when would you use them?',
        'Explain context managers and `with` statement internals.',
        'How does Python GIL impact concurrency?',
        'When to use threading, multiprocessing, and asyncio?',
        'How do you structure a production-ready Python package?',
        'How do you write performant database code in Django/FastAPI stacks?',
        'How do you profile and optimize CPU/memory heavy Python code?',
        'How would you design scalable background job processing in Python?',
        'How do you enforce reliability with tests, typing, and CI/CD in Python apps?',
    ],
    'GEN_AI': [
        'What is the difference between LLM pretraining, fine-tuning, and prompting?',
        'Explain tokens, context window, and temperature in LLMs.',
        'What is retrieval-augmented generation (RAG) and when should it be used?',
        'How do embeddings and vector stores work together?',
        'How do you evaluate answer quality in GenAI systems?',
        'How do you reduce hallucinations in production assistants?',
        'How would you design prompt templates with guardrails?',
        'How do you implement grounding and citation strategy in RAG?',
        'How do you manage latency and cost for LLM inference?',
        'How do you monitor safety and prompt-injection risks?',
        'How would you design an agentic workflow for multi-step tasks?',
        'How do you select between open-source and hosted models for enterprise use?',
    ],
    'JAVA': [
        'Explain OOP principles in Java with real examples.',
        'Difference between `ArrayList` and `LinkedList`.',
        'How does exception handling hierarchy work in Java?',
        'What are generics and why are they important?',
        'Explain Java memory model and garbage collection basics.',
        'How do streams and lambda expressions improve code quality?',
        'How does multithreading and synchronization work in Java?',
        'How would you optimize a Spring Boot API endpoint?',
        'How do JPA/Hibernate fetch strategies impact performance?',
        'How do you design transaction-safe service layers in Java?',
        'How would you scale Java microservices with observability?',
        'How do you design resilient distributed systems in Java (circuit breaker/retry)?',
    ],
    'ANGULAR': [
        'Explain Angular module, component, template architecture.',
        'Difference between template-driven and reactive forms.',
        'How does dependency injection work in Angular?',
        'How do observables and RxJS operators work in Angular apps?',
        'How does Angular change detection work?',
        'How would you structure reusable shared modules and services?',
        'How do route guards and lazy loading improve app security/performance?',
        'How do you manage state in Angular applications?',
        'How do you optimize bundle size and startup performance in Angular?',
        'How do you write robust unit/integration tests for Angular components?',
        'How would you handle large enterprise forms with validation complexity?',
        'How do you design Angular frontend for scalable API integration and error handling?',
    ],
    'DOTNET': [
        'Explain CLR, CTS, and managed code in .NET.',
        'Difference between value types and reference types in C#.',
        'How does async/await work in .NET?',
        'How do dependency injection and middleware work in ASP.NET Core?',
        'How do you build clean layered architecture in .NET apps?',
        'How do Entity Framework tracking and migrations work?',
        'How do you secure ASP.NET APIs with JWT and policy-based auth?',
        'How do you optimize performance in ASP.NET Core endpoints?',
        'How do you design background jobs and hosted services in .NET?',
        'How do you implement logging, tracing, and observability in .NET?',
        'How would you design scalable microservices using .NET and message queues?',
        'How do you apply domain-driven design in complex .NET systems?',
    ],
}


def extract_resume_text(uploaded_file):
    if not uploaded_file:
        return ''

    name = uploaded_file.name.lower()
    suffix = Path(name).suffix

    if suffix == '.pdf':
        try:
            from pypdf import PdfReader

            reader = PdfReader(uploaded_file)
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text() or '')
            return '\n'.join(text_parts).strip()
        except Exception:
            uploaded_file.seek(0)

    try:
        content = uploaded_file.read()
        if isinstance(content, bytes):
            return content.decode('utf-8', errors='ignore').strip()
        return str(content).strip()
    finally:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass


def _top_keywords(resume_text, max_items=8):
    words = re.findall(r'[A-Za-z][A-Za-z0-9+#.]{1,20}', (resume_text or '').lower())
    stopwords = {
        'the', 'and', 'with', 'for', 'from', 'this', 'that', 'have', 'has', 'you', 'your',
        'are', 'was', 'were', 'will', 'using', 'used', 'into', 'over', 'under', 'year', 'years',
        'project', 'projects', 'worked', 'work', 'team', 'skills', 'skill', 'experience', 'role',
        'education', 'college', 'university', 'resume', 'profile', 'developer', 'engineer',
    }

    freq = {}
    for word in words:
        if len(word) < 3 or word in stopwords:
            continue
        freq[word] = freq.get(word, 0) + 1

    ranked = sorted(freq.items(), key=lambda item: (-item[1], item[0]))
    return [item[0] for item in ranked[:max_items]]


def _clean_text(value):
    return re.sub(r'\s+', ' ', (value or '').strip())


def _unique_preserve(items):
    seen = set()
    output = []
    for item in items:
        key = item.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item.strip())
    return output


def _split_bullets(resume_text):
    raw_lines = [line.strip(' •\t-') for line in (resume_text or '').splitlines()]
    clean_lines = [_clean_text(line) for line in raw_lines if _clean_text(line)]
    return clean_lines


def _extract_skills_from_text(resume_text):
    lines = _split_bullets(resume_text)
    skill_lines = [line for line in lines if 'skill' in line.lower() or 'technology' in line.lower() or 'tools' in line.lower()]
    extracted = []

    for line in skill_lines:
        normalized = re.sub(r'(?i)skills?|technologies|tools|frameworks|languages', '', line)
        parts = re.split(r'[:,|/]|\s{2,}', normalized)
        for part in parts:
            token = _clean_text(part)
            if token and len(token) <= 35:
                extracted.append(token)

    if not extracted:
        extracted = _top_keywords(resume_text, max_items=12)

    return _unique_preserve(extracted)[:12]


def _extract_project_lines(resume_text):
    lines = _split_bullets(resume_text)
    project_tokens = ['project', 'built', 'developed', 'implemented', 'designed', 'deployed', 'api', 'backend', 'frontend']
    project_lines = [line for line in lines if any(token in line.lower() for token in project_tokens)]
    return _unique_preserve(project_lines)[:10]


def _extract_internship_lines(resume_text):
    lines = _split_bullets(resume_text)
    intern_tokens = ['intern', 'internship', 'trainee', 'apprentice']
    internship_lines = [line for line in lines if any(token in line.lower() for token in intern_tokens)]
    return _unique_preserve(internship_lines)[:8]


def _extract_resume_signals(resume_text):
    internship_lines = _extract_internship_lines(resume_text)
    project_lines = _extract_project_lines(resume_text)
    normalized_skills = _extract_skills_from_text(resume_text)
    fallback_keywords = _top_keywords(resume_text, max_items=14)

    if not normalized_skills:
        normalized_skills = fallback_keywords[:8]

    return internship_lines, project_lines, normalized_skills, fallback_keywords


def _add_unique_question(target, question, seen):
    clean = (question or '').strip()
    if clean and clean not in seen:
        target.append(clean)
        seen.add(clean)


def _normalize_role_track(target_role):
    role = (target_role or '').strip().upper()
    if role in ROLE_QUESTION_BANK:
        return role
    return 'PYTHON'


def _role_question_set(target_role):
    role_key = _normalize_role_track(target_role)
    return _expanded_role_question_bank(role_key), ROLE_LABELS.get(role_key, 'Python Developer')


def _question_core_text(question):
    clean = (question or '').strip().rstrip('?.!')
    return clean


def _expanded_role_question_bank(role_key):
    base_questions = ROLE_QUESTION_BANK.get(role_key, ROLE_QUESTION_BANK['PYTHON'])

    expanded = []
    seen = set()

    def _push(item):
        text = (item or '').strip()
        if text and text not in seen:
            expanded.append(text)
            seen.add(text)

    variation_templates = [
        'Give one real project example where you applied: {core}.',
        'What trade-offs do you consider in production while working on: {core}?',
        'What are common mistakes in {core}, and how do you avoid them?',
        'How would you explain and defend your approach to {core} in an interview?',
        'How would you optimize performance and scalability for: {core}?',
        'How would you test and validate implementation quality for: {core}?',
        'What security or reliability risks do you evaluate while implementing: {core}?',
        'If requirements change suddenly, how would you adapt your approach to: {core}?',
    ]

    for base in base_questions:
        _push(base)
        core = _question_core_text(base)
        for template in variation_templates:
            _push(template.format(core=core).strip())

    core_topics = [_question_core_text(item) for item in base_questions if _question_core_text(item)]
    synthesis_templates = [
        'What architecture pattern would you choose for {core}, and why?',
        'How would you debug a production issue related to {core}?',
        'How do you monitor and measure success for {core} in production?',
        'How do you document and communicate decisions around {core} in a team?',
        'What failure scenarios do you plan for while implementing {core}?',
        'How would you design an interview-quality solution for {core} from scratch?',
    ]

    idx = 0
    while len(expanded) < 100 and core_topics:
        core = core_topics[idx % len(core_topics)]
        template = synthesis_templates[idx % len(synthesis_templates)]
        _push(template.format(core=core))
        idx += 1

    return expanded


def _finalize_random_question_set(all_questions, role_anchor_questions, max_items, excluded_questions=None):
    excluded_set = {item.strip() for item in (excluded_questions or []) if isinstance(item, str) and item.strip()}
    role_anchor_set = set(role_anchor_questions)
    role_bucket = [q for q in all_questions if q in role_anchor_set]
    contextual_bucket = [q for q in all_questions if q not in role_anchor_set]

    random.shuffle(role_bucket)
    random.shuffle(contextual_bucket)

    role_fresh = [q for q in role_bucket if q not in excluded_set]
    contextual_fresh = [q for q in contextual_bucket if q not in excluded_set]
    role_repeat = [q for q in role_bucket if q in excluded_set]
    contextual_repeat = [q for q in contextual_bucket if q in excluded_set]

    selected = []
    selected_set = set()

    def _take(source, count):
        for item in source:
            if len(selected) >= count:
                break
            if item in selected_set:
                continue
            selected.append(item)
            selected_set.add(item)

    # Keep strong role depth + resume/context blend with priority to unseen questions.
    role_target = min(int(max_items * 0.7), len(role_fresh))
    _take(role_fresh, role_target)

    if len(selected) < max_items:
        _take(contextual_fresh, max_items)
    if len(selected) < max_items:
        _take(role_fresh[role_target:], max_items)
    if len(selected) < max_items:
        _take(role_repeat, max_items)
    if len(selected) < max_items:
        _take(contextual_repeat, max_items)

    return selected[:max_items]


def extract_resume_role_match(resume_text, top_k=14):
    text = (resume_text or '').strip().lower()
    if not text:
        return {
            'keywords': [],
            'role_scores': {key: 0 for key in ROLE_QUESTION_BANK.keys()},
            'best_role': 'PYTHON',
        }

    keywords = _top_keywords(text, max_items=max(8, top_k))
    keyword_set = set(keywords)

    role_scores = {}
    for role_key, role_questions in ROLE_QUESTION_BANK.items():
        role_text = ' '.join(role_questions).lower()
        role_tokens = set(_top_keywords(role_text, max_items=40))
        role_scores[role_key] = len(keyword_set.intersection(role_tokens))

    best_role = max(role_scores.items(), key=lambda item: item[1])[0] if role_scores else 'PYTHON'
    if role_scores.get(best_role, 0) == 0:
        best_role = 'PYTHON'

    return {
        'keywords': keywords,
        'role_scores': role_scores,
        'best_role': best_role,
    }


def _get_flan_pipeline():
    global _FLAN_PIPELINE
    if _FLAN_PIPELINE is not None:
        return _FLAN_PIPELINE

    with _FLAN_INIT_LOCK:
        if _FLAN_PIPELINE is not None:
            return _FLAN_PIPELINE

        try:
            from transformers import pipeline

            _FLAN_PIPELINE = pipeline(
                'text2text-generation',
                model='google/flan-t5-large',
                device=-1,
            )
        except Exception:
            _FLAN_PIPELINE = None

    return _FLAN_PIPELINE


def _parse_generated_questions(raw_text):
    lines = [line.strip() for line in (raw_text or '').splitlines() if line.strip()]
    cleaned = []
    seen = set()

    for line in lines:
        normalized = re.sub(r'^\d+[\).\-:\s]*', '', line).strip()
        if not normalized.endswith('?'):
            normalized = normalized.rstrip('.') + '?'
        if len(normalized) < 20:
            continue
        if normalized not in seen:
            cleaned.append(normalized)
            seen.add(normalized)

    return cleaned


def generate_questions_with_flan(resume_text, target_role='PYTHON', question_count=20):
    role_key = _normalize_role_track(target_role)
    role_label = ROLE_LABELS.get(role_key, 'Python Developer')
    keywords = _top_keywords(resume_text or '', max_items=10)
    keyword_text = ', '.join(keywords) if keywords else 'projects, problem solving, implementation'

    flan = _get_flan_pipeline()
    if flan is None:
        return []

    prompt = (
        f"Generate {question_count} technical interview questions for a {role_label} candidate. "
        f"Use resume context and role-specific depth. "
        f"Resume keywords: {keyword_text}. "
        "Questions must be practical, interview-valid, and concise. "
        "Return only numbered questions, one per line."
    )

    try:
        output = flan(
            prompt,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            num_return_sequences=1,
        )
    except Exception:
        return []

    if not output:
        return []

    generated_text = output[0].get('generated_text', '')
    return _parse_generated_questions(generated_text)[:question_count]


def generate_role_based_questions(resume_text, target_role='PYTHON', exclude_questions=None, question_count=20):
    flan_questions = generate_questions_with_flan(
        resume_text=resume_text,
        target_role=target_role,
        question_count=question_count,
    )

    if len(flan_questions) >= question_count:
        return _finalize_random_question_set(
            flan_questions,
            flan_questions,
            question_count,
            excluded_questions=exclude_questions,
        )

    fallback = generate_resume_based_questions(
        resume_text=resume_text,
        target_role=target_role,
        exclude_questions=exclude_questions,
        question_count=question_count,
    )

    combined = []
    seen = set()
    for item in flan_questions + fallback:
        clean = (item or '').strip()
        if clean and clean not in seen:
            combined.append(clean)
            seen.add(clean)

    return combined[:question_count]


def generate_resume_based_questions(resume_text, target_role='PYTHON', exclude_questions=None, question_count=20):
    text = (resume_text or '').strip()

    role_questions, role_label = _role_question_set(target_role)
    target_min = max(20, int(question_count or 20))
    target_max = target_min

    if not text:
        sampled = role_questions[:]
        random.shuffle(sampled)
        return _finalize_random_question_set(sampled, sampled, target_max, excluded_questions=exclude_questions)

    internships, projects, skills, keywords = _extract_resume_signals(text)

    questions = []
    seen = set()

    role_seeded = role_questions[:]
    random.shuffle(role_seeded)
    role_seeded = role_seeded[: min(70, len(role_seeded))]

    for role_question in role_seeded:
        _add_unique_question(questions, role_question, seen)

    # Core contextual openers
    _add_unique_question(
        questions,
        'Walk me through your resume in 90 seconds, focusing on internships, projects, and role-fit depth.',
        seen,
    )
    _add_unique_question(
        questions,
        'Which one experience in your resume best represents your problem-solving ability, and why?',
        seen,
    )

    for line in internships:
        excerpt = _clean_text(line[:120])
        _add_unique_question(
            questions,
            f"From your internship experience '{excerpt}', what was your exact ownership and measurable outcome?",
            seen,
        )
        _add_unique_question(
            questions,
            f"During '{excerpt}', what technical challenge did you face and how did you solve it end-to-end?",
            seen,
        )
        _add_unique_question(
            questions,
            f"What would you improve in the internship work described as '{excerpt}' if you had two more sprints?",
            seen,
        )

    for line in projects:
        excerpt = _clean_text(line[:120])
        _add_unique_question(
            questions,
            f"From your project '{excerpt}', explain architecture, stack decisions, and your exact contribution.",
            seen,
        )
        _add_unique_question(
            questions,
            f"If this project '{excerpt}' scales to 10x traffic, what redesign steps would you take?",
            seen,
        )
        _add_unique_question(
            questions,
            f"What testing and monitoring strategy did (or would) you apply for project '{excerpt}'?",
            seen,
        )

    for skill in skills:
        skill_clean = _clean_text(skill)
        _add_unique_question(
            questions,
            f"Your resume lists '{skill_clean}'. Where exactly did you apply it and what business/user impact did it create?",
            seen,
        )
        _add_unique_question(
            questions,
            f"What are common pitfalls while using '{skill_clean}', and how did you avoid them in your implementation?",
            seen,
        )
        _add_unique_question(
            questions,
            f"Rate your proficiency in '{skill_clean}' from 1–10 and justify with one concrete example from your resume.",
            seen,
        )

    keyword_pairs = []
    for idx in range(0, len(keywords) - 1, 2):
        keyword_pairs.append((keywords[idx], keywords[idx + 1]))

    for left, right in keyword_pairs:
        _add_unique_question(
            questions,
            f"You mention '{left}' and '{right}' in your resume. Describe a scenario where both were used together.",
            seen,
        )

    for keyword in keywords:
        _add_unique_question(
            questions,
            f"Explain one advanced concept in '{keyword}' that you have practically used based on your resume experience.",
            seen,
        )

    # Cross-cutting engineering depth questions based on resume evidence.
    _add_unique_question(
        questions,
        'Pick one project from your resume and explain its API design, database schema choices, and performance considerations.',
        seen,
    )
    _add_unique_question(
        questions,
        'Describe a production bug (or major issue) from your internship/project experience and your debugging timeline.',
        seen,
    )
    _add_unique_question(
        questions,
        'What trade-offs did you make between speed of delivery and code quality in your listed projects?',
        seen,
    )
    _add_unique_question(
        questions,
        'How do you prioritize features when requirements are unclear, based on your resume experience?',
        seen,
    )

    # Ensure minimum question count while staying resume-dependent via extracted signals.
    while len(questions) < target_min and keywords:
        pivot = keywords[len(questions) % len(keywords)]
        _add_unique_question(
            questions,
            f"Based on your resume, how would you teach '{pivot}' to a new team member with a real example from your work?",
            seen,
        )

    if len(questions) < target_min:
        while len(questions) < target_min:
            _add_unique_question(
                questions,
                'Walk me through the most impactful technical achievement mentioned in your resume with metrics.',
                seen,
            )

    return _finalize_random_question_set(
        questions,
        role_seeded,
        target_max,
        excluded_questions=exclude_questions,
    )
