"""Detectors for languages, frameworks, CI, infra, and tools"""
import os
import json


def _read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def make_detection(name, confidence, sources):
    return {
        'name': name,
        'confidence': round(float(confidence), 2),
        'sources': sorted(list(set(sources)))
    }


def detect_languages(files):
    seen = {}
    for f in files:
        if f.endswith('.py') and 'Python' not in seen:
            seen['Python'] = make_detection('Python', 0.95, [f])
        elif f.endswith('.js') and 'JavaScript' not in seen:
            seen['JavaScript'] = make_detection('JavaScript', 0.9, [f])
        elif f.endswith('.ts') and 'TypeScript' not in seen:
            seen['TypeScript'] = make_detection('TypeScript', 0.9, [f])
        elif f.endswith('.go') and 'Go' not in seen:
            seen['Go'] = make_detection('Go', 0.95, [f])
        elif f.endswith('.java') and 'Java' not in seen:
            seen['Java'] = make_detection('Java', 0.9, [f])
        elif f.endswith('.cs') and 'C#' not in seen:
            seen['C#'] = make_detection('C#', 0.9, [f])
        elif f.endswith('.rb') and 'Ruby' not in seen:
            seen['Ruby'] = make_detection('Ruby', 0.9, [f])
    return sorted(seen.values(), key=lambda d: d['name'])


def detect_package_managers(files):
    results = []
    names = set(files)
    if 'package.json' in names:
        results.append(make_detection('npm / package.json', 0.95, ['package.json']))
    if 'yarn.lock' in names:
        results.append(make_detection('yarn', 0.9, ['yarn.lock']))
    if 'pnpm-lock.yaml' in names:
        results.append(make_detection('pnpm', 0.9, ['pnpm-lock.yaml']))
    if 'package-lock.json' in names:
        results.append(make_detection('npm (package-lock)', 0.9, ['package-lock.json']))
    if 'requirements.txt' in names or 'pyproject.toml' in names:
        src = 'requirements.txt' if 'requirements.txt' in names else 'pyproject.toml'
        results.append(make_detection('pip / pyproject', 0.9, [src]))
    if 'go.mod' in names:
        results.append(make_detection('go modules', 0.95, ['go.mod']))
    if 'pom.xml' in names:
        results.append(make_detection('maven', 0.9, ['pom.xml']))
    if 'Gemfile' in names:
        results.append(make_detection('bundler', 0.9, ['Gemfile']))
    return sorted(results, key=lambda d: d['name'])


def detect_ci(path):
    cis = []
    gh = os.path.join(path, '.github', 'workflows')
    if os.path.isdir(gh):
        cis.append(make_detection('GitHub Actions', 0.95, ['.github/workflows']))
    if os.path.exists(os.path.join(path, '.gitlab-ci.yml')):
        cis.append(make_detection('GitLab CI', 0.95, ['.gitlab-ci.yml']))
    if os.path.exists(os.path.join(path, 'azure-pipelines.yml')):
        cis.append(make_detection('Azure Pipelines', 0.95, ['azure-pipelines.yml']))
    return sorted(cis, key=lambda d: d['name'])


def detect_infra(files, path):
    infra = []
    names = set(files)
    if 'Dockerfile' in names:
        infra.append(make_detection('Docker', 0.95, ['Dockerfile']))
    if 'docker-compose.yml' in names:
        infra.append(make_detection('Docker Compose', 0.9, ['docker-compose.yml']))
    tf_files = [f for f in files if f.endswith('.tf')]
    if tf_files:
        infra.append(make_detection('Terraform', 0.95, tf_files))
    return sorted(infra, key=lambda d: d['name'])


def detect_tools(files):
    tools = {}
    # Look for common tools by filename or extensions
    for f in files:
        if f in ('pytest.ini', 'tox.ini'):
            tools['pytest/tox'] = tools.get('pytest/tox', []) + [f]
        if f in ('.eslintrc', '.eslintrc.json'):
            tools['ESLint'] = tools.get('ESLint', []) + [f]
        if f in ('prettier.config.js', '.prettierrc'):
            tools['Prettier'] = tools.get('Prettier', []) + [f]
    return sorted([make_detection(name, 0.85, srcs) for name, srcs in tools.items()], key=lambda d: d['name'])


def detect_frameworks_from_package_json(path):
    pkg = _read_json(path)
    deps = {}
    deps.update(pkg.get('dependencies', {}))
    deps.update(pkg.get('devDependencies', {}))
    frameworks = []
    keys = set(deps.keys())
    if 'react' in keys:
        frameworks.append(make_detection('React', 0.95, ['package.json']))
    if 'next' in keys or 'next.js' in keys:
        frameworks.append(make_detection('Next.js', 0.95, ['package.json']))
    if 'express' in keys:
        frameworks.append(make_detection('Express', 0.9, ['package.json']))
    if 'gatsby' in keys:
        frameworks.append(make_detection('Gatsby', 0.9, ['package.json']))
    if '@angular/core' in keys:
        frameworks.append(make_detection('Angular', 0.95, ['package.json']))
    if 'vue' in keys or any(k.startswith('@vue') for k in keys):
        frameworks.append(make_detection('Vue', 0.95, ['package.json']))
    return frameworks


def detect_python_frameworks_from_requirements(path):
    frameworks = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().lower()
            if 'django' in text:
                frameworks.append(make_detection('Django', 0.9, ['requirements.txt']))
            if 'flask' in text:
                frameworks.append(make_detection('Flask', 0.9, ['requirements.txt']))
            if 'fastapi' in text:
                frameworks.append(make_detection('FastAPI', 0.9, ['requirements.txt']))
            if 'pytest' in text:
                frameworks.append(make_detection('pytest', 0.75, ['requirements.txt']))
    except Exception:
        pass
    return frameworks


def detect_cloud_sdks(files, path):
    detections = {}
    names = set(files)
    # Node / JavaScript package.json inspection
    if 'package.json' in names:
        pkg = _read_json(os.path.join(path, 'package.json'))
        deps = {}
        deps.update(pkg.get('dependencies', {}))
        deps.update(pkg.get('devDependencies', {}))
        keys = set(deps.keys())
        if 'aws-sdk' in keys or any(k.startswith('@aws-sdk') for k in keys):
            detections['AWS SDK'] = detections.get('AWS SDK', set()) | {'package.json'}
        if any(k.startswith('@google-cloud') or k.startswith('google-') for k in keys):
            detections['GCP SDK'] = detections.get('GCP SDK', set()) | {'package.json'}
        if any(k.startswith('@azure') or k.startswith('azure-') for k in keys):
            detections['Azure SDK'] = detections.get('Azure SDK', set()) | {'package.json'}
    # Python requirements inspection
    if 'requirements.txt' in names:
        try:
            with open(os.path.join(path, 'requirements.txt'), 'r', encoding='utf-8') as f:
                txt = f.read().lower()
                if 'boto3' in txt:
                    detections['AWS SDK (boto3)'] = detections.get('AWS SDK (boto3)', set()) | {'requirements.txt'}
                if 'google-cloud' in txt or 'google-cloud-storage' in txt or 'google-storage' in txt:
                    detections['GCP SDK (google-cloud)'] = detections.get('GCP SDK (google-cloud)', set()) | {'requirements.txt'}
                if 'azure' in txt or 'azure-storage' in txt or 'azure-identity' in txt:
                    detections['Azure SDK (azure)'] = detections.get('Azure SDK (azure)', set()) | {'requirements.txt'}
        except Exception:
            pass
    # Go modules inspection
    if 'go.mod' in names:
        try:
            with open(os.path.join(path, 'go.mod'), 'r', encoding='utf-8') as f:
                gm = f.read()
                if 'github.com/aws/aws-sdk-go' in gm:
                    detections['AWS SDK for Go'] = detections.get('AWS SDK for Go', set()) | {'go.mod'}
                if 'cloud.google.com/go' in gm:
                    detections['GCP SDK for Go'] = detections.get('GCP SDK for Go', set()) | {'go.mod'}
        except Exception:
            pass
    # Terraform provider heuristics
    for f in files:
        if f.endswith('.tf'):
            try:
                content = open(os.path.join(path, f), 'r', encoding='utf-8').read().lower()
                if 'provider "aws"' in content or 'provider = "aws"' in content:
                    detections['AWS (Terraform provider)'] = detections.get('AWS (Terraform provider)', set()) | {f}
                if 'provider "google"' in content or 'provider = "google"' in content:
                    detections['GCP (Terraform provider)'] = detections.get('GCP (Terraform provider)', set()) | {f}
                if 'provider "azurerm"' in content or 'provider = "azurerm"' in content:
                    detections['Azure (Terraform provider)'] = detections.get('Azure (Terraform provider)', set()) | {f}
            except Exception:
                pass
    # Convert to structured detections
    results = []
    for name, srcs in detections.items():
        # Confidence heuristic: manifest-based -> high
        conf = 0.95
        results.append(make_detection(name, conf, list(srcs)))
    return sorted(results, key=lambda d: d['name'])


def detect_project(path):
    info = {
        'name': os.path.basename(path),
        'path': os.path.abspath(path),
        'languages': [],
        'frameworks': [],
        'package_managers': [],
        'ci': [],
        'infra': [],
        'tools': [],
        'files_found': [],
        'cloud_sdks': [],
    }

    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            files.append(f)
    info['files_found'] = sorted(set(files))

    info['languages'] = detect_languages(files)
    info['package_managers'] = detect_package_managers(files)
    info['ci'] = detect_ci(path)
    info['infra'] = detect_infra(files, path)
    info['tools'] = detect_tools(files)

    frameworks = []
    if 'package.json' in files:
        frameworks.extend(detect_frameworks_from_package_json(os.path.join(path, 'package.json')))
    if 'requirements.txt' in files:
        frameworks.extend(detect_python_frameworks_from_requirements(os.path.join(path, 'requirements.txt')))
    # quick checks
    if 'managed' in files:
        pass

    info['frameworks'] = sorted(frameworks, key=lambda d: d['name'])
    info['cloud_sdks'] = detect_cloud_sdks(info['files_found'], path)
    return info
