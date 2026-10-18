"""Keep every prior unreceipted attempt immutable during RTL test resumption.

This module validates evidence IO only. It does not grant resource admission,
execute a compiler, or qualify RTL from the existence of a binary.
"""
import gzip
import hashlib
from pathlib import Path


def attempt_directory(root, label):
    root = Path(root)
    assert label and all(c.isalnum() or c == '_' for c in label)
    # A compressed interrupted executable can exist without its original VVP.
    # Logs and incomplete archives must also survive a new attempt unchanged.
    if not any(root.glob(label + '*')):
        return root
    attempts = root / 'attempts'
    attempts.mkdir(exist_ok=True)
    for revision in range(1, 10001):
        candidate = attempts / f'{label}-r{revision}'
        try:
            candidate.mkdir()
        except FileExistsError:
            continue
        return candidate
    raise RuntimeError('too many retained attempts; select a new output revision')


def verify_binary_archive(row, default=None):
    archive = row.get('exact_binary_archive', row.get('archive', default))
    assert archive is not None, 'accepted binary archive identity missing'
    assert len(row['binary_sha256']) == 64
    with gzip.open(archive, 'rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert digest == row['binary_sha256'], 'accepted binary bytes changed'
