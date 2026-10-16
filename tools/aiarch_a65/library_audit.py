"""CPU-only installed RECORD and official cached wheel identity qualification."""
import base64
import csv
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import os
from urllib.parse import urlparse, unquote
from paths import OLD, R, save, sha


def main():
    site = OLD / 'venv/lib/python3.10/site-packages'
    files = 0
    bytecode_rewrites = []
    distributions = 0
    for directory in site.glob('*.dist-info'):
        if directory.is_symlink():
            continue  # Frozen core runtime is separately SHA/mtime verified against A61 bindings.
        record = directory / 'RECORD'
        for rel, hash_value, size in csv.reader(record.open()):
            if not hash_value:
                continue
            algorithm, expected = hash_value.split('=', 1)
            assert algorithm == 'sha256'
            path = site / rel
            actual = base64.urlsafe_b64encode(bytes.fromhex(sha(path))).decode().rstrip('=')
            if actual != expected:
                assert path.suffix == '.pyc', 'INSTALLED_SOURCE_OR_BINARY_RECORD_MISMATCH ' + str(path)
                bytecode_rewrites.append(str(path))
                continue
            if size:
                assert path.stat().st_size == int(size)
            files += 1
        distributions += 1
    save('bytecode_rewrite_paths.json', bytecode_rewrites)
    env = os.environ.copy(); env['LD_LIBRARY_PATH']='/data/c16/env/cpython-3.10.12/lib'
    proof = subprocess.check_output(['/data/c16/env/cpython-3.10.12/bin/python3.10', '-S', str(Path(__file__).with_name('pyc_source_audit.py')), str(R/'bytecode_rewrite_paths.json')], env=env, text=True)
    value=json.loads(proof); assert value['status']=='PASS'
    save('bytecode_source_identity.json', value)
    report = json.loads((OLD / 'environment_install_report.json').read_text())
    wheels = []
    for row in report['install']:
        data = row['download_info']
        path = Path(unquote(urlparse(data['url']).path))
        if not path.exists():
            path = OLD / 'downloads' / path.name
        expected = data['archive_info'].get('hash', '')
        if not expected:
            expected = 'sha256=' + data['archive_info']['hashes']['sha256']
        algorithm, value = expected.split('=', 1)
        assert algorithm == 'sha256' and sha(path) == value, str(path)
        wheels.append({'name': row['metadata']['name'], 'version': row['metadata']['version'],
                       'wheel_SHA256': value})
    save('library_RECORD_' + ('post' if '--post' in sys.argv else 'pre') + '.json',
         {'status': 'PASS', 'actual_installed_RECORD_files_verified': files,
          'A61_owned_distributions': distributions, 'installed_bytecode_regeneration_proof': value, 'frozen_official_wheels': wheels,
          'Torch_imports': 0, 'CUDA_initializations': 0, 'installs': 0, 'downloads': 0})
    print('PASS_LIBRARY_RECORD_AND_OFFICIAL_CACHED_WHEELS', files, distributions, len(wheels), flush=True)


if __name__ == '__main__':
    main()
