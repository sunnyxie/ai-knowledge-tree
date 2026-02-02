"""Scanning logic for projects"""
import os
import time
from .detectors import detect_project


def is_project_dir(path):
    # Heuristic: contains at least one known manifest or a .git directory
    manifests = ["package.json", "requirements.txt", "pyproject.toml", "pom.xml", "go.mod", "Dockerfile", "docker-compose.yml", "Gemfile", "composer.json", "main.tf"]
    for m in manifests:
        if os.path.exists(os.path.join(path, m)):
            return True
    if os.path.isdir(os.path.join(path, ".git")):
        return True
    # also if contains any file with known extension (include Terraform files)
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(('.py', '.js', '.ts', '.java', '.go', '.cs', '.tf', 'Dockerfile')):
                return True
        break
    return False


def list_candidate_projects(root):
    # Look at top-level directories; also consider root itself
    candidates = []
    if is_project_dir(root):
        candidates.append(root)
    try:
        for entry in os.scandir(root):
            if entry.is_dir():
                if is_project_dir(entry.path):
                    candidates.append(entry.path)
    except FileNotFoundError:
        return []
    return candidates


def scan_root(root):
    projects = []
    candidates = list_candidate_projects(root)
    for p in candidates:
        info = detect_project(p)
        projects.append(info)
    return {
        "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "root": os.path.abspath(root),
        "projects": projects,
    }
