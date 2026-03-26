# Knowledge Tree Agent
# This project is a experiment, 99% of the code was created by AI.

Scans a root directory of projects and produces a JSON "knowledge tree" per project, reporting detected languages, frameworks, package managers, CI, infra, and tooling.

Usage:

```bash
python -m knowledge_tree.cli scan /path/to/projects --output json
```

Output: JSON printed to stdout.

The implementation is intentionally minimal and uses heuristics based on manifest files and common filenames.

It also detects common **Cloud SDKs** (AWS, GCP, Azure) by inspecting package manifests, `requirements.txt`, `go.mod`, and Terraform (`*.tf`) files.

Detections are now returned as structured objects with the keys `name`, `confidence` (0-1 float), and `sources` (files that led to the detection).

Continuous Integration (GitHub Actions): a workflow (`.github/workflows/python-tests.yml`) runs `pytest` on push and pull requests. To run tests locally:

```bash
pip install --user -r requirements.txt
pip install --user -e .
pytest
```
