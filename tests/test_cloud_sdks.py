import os
import json
from knowledge_tree.scanner import scan_root


def test_detect_aws_node_and_python(tmp_path):
    # Node project with aws-sdk and Python project with boto3
    proj = tmp_path / "node-aws"
    proj.mkdir()
    (proj / "package.json").write_text('{"dependencies": {"aws-sdk": "^2.0.0"}}')

    pyproj = tmp_path / "py-aws"
    pyproj.mkdir()
    (pyproj / "requirements.txt").write_text('boto3>=1.0.0')

    res = scan_root(str(tmp_path))
    names = {p['name']: p for p in res['projects']}
    assert 'node-aws' in names
    # cloud_sdks is now a list of detection dicts
    assert any('aws' in d.get('name').lower() for d in names['node-aws']['cloud_sdks'])
    assert 'py-aws' in names
    assert any('boto' in d.get('name').lower() or 'aws' in d.get('name').lower() for d in names['py-aws']['cloud_sdks'])


def test_detect_gcp_from_terraform_and_go(tmp_path):
    proj = tmp_path / "infra-gcp"
    proj.mkdir()
    (proj / "main.tf").write_text('provider "google" { project = "my" }')

    proj2 = tmp_path / "go-gcp"
    proj2.mkdir()
    (proj2 / "go.mod").write_text('module example\n\nrequire cloud.google.com/go v0.0.0')

    res = scan_root(str(tmp_path))
    names = {p['name']: p for p in res['projects']}
    assert 'infra-gcp' in names
    assert any('gcp' in d.get('name').lower() or 'google' in d.get('name').lower() for d in names['infra-gcp']['cloud_sdks'])
    assert 'go-gcp' in names
    assert any('gcp' in d.get('name').lower() or 'google' in d.get('name').lower() for d in names['go-gcp']['cloud_sdks'])
