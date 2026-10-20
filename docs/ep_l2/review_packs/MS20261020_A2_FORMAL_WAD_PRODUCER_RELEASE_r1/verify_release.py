"""Read-only producer evidence verification. No build, simulation, or E mutation."""
import hashlib
import json
from pathlib import Path

PACK = Path(__file__).resolve().parent


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    checked = {}

    def refs(node):
        if isinstance(node, dict):
            if 'path' in node and 'sha256' in node and str(node['path']).startswith('/'):
                path = node['path']
                actual = checked.setdefault(path, sha(path))
                assert actual == node['sha256'], 'Changed reference: ' + path
            for value in node.values():
                refs(value)
        elif isinstance(node, list):
            for value in node:
                refs(value)

    release = json.loads((PACK/'RELEASE.json').read_text())
    assert release['status'] == 'FORMALLY_RELEASED_BY_A2_FOR_E_INDEPENDENT_ACCEPTANCE'
    assert sha(release['binary_path']) == release['source_identity']['binary_sha256']
    for path in PACK.glob('*.json'):
        refs(json.loads(path.read_text()))
    manifest = json.loads((PACK/'NATIVE_EVIDENCE_MANIFEST.json').read_text())
    assert len(manifest['tests']) == 17
    assert sum(len(t['terminal_checks']) for t in manifest['tests']) == 26
    for t in manifest['tests']:
        assert t['actual_exit'] == 0 and t['expectation_verified']
        assert sha(t['command'][0]) == t['binary_sha256']
        assert sha(t['receipt_path']) == t['receipt_sha256']
        assert sha(t['raw_log']) == t['raw_log_sha256']
        raw = Path(t['raw_log']).read_text()
        assert all(ok and text in raw for text, ok in t['terminal_checks'].items())
    print(json.dumps(dict(status='RELEASE_IDENTITIES_AND_RETAINED_E_NATIVE_EVIDENCE_VERIFIED',
        release_sha256=sha(PACK/'RELEASE.json'),references_checked=len(checked),
        consumed_E_native_commands=17,terminal_checks=26,new_native_runs=0,
        new_application_starts=0,application_qualification='E_OWNED_PENDING')))


if __name__ == '__main__':
    main()
