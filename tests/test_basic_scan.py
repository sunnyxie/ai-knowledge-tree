import os
import json
import tempfile
from knowledge_tree.scanner import scan_root


def test_basic_scan(tmp_path):
    # create a fake project folder with package.json and a Dockerfile
    proj = tmp_path / "my-node-app"
    proj.mkdir()
    (proj / "package.json").write_text('{"name": "my-app", "dependencies": {"react": "^18.0.0"}}')
    (proj / "Dockerfile").write_text('FROM node:16')

    result = scan_root(str(tmp_path))
    assert result['root'] == str(tmp_path)
    projects = result['projects']
    assert len(projects) == 1
    p = projects[0]
    assert p['name'] == 'my-node-app'
    assert any(f.get('name') == 'React' for f in p['frameworks'])
    assert any(i.get('name') == 'Docker' for i in p['infra'])
    assert any(pm.get('name') == 'npm / package.json' for pm in p['package_managers'])
    # ensure structured detection shape
    assert isinstance(p['frameworks'][0]['confidence'], float)
    assert isinstance(p['frameworks'][0]['sources'], list)
