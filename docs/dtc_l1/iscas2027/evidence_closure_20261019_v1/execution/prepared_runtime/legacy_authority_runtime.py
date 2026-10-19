"""PREPARED_NOT_TESTED. Exact frozen AG4 read-only authority procedures.

Extract only named functions/constants from SHA-bound original source text.
Original CLI/import side effects are never run. No foreign or old raw is read;
history/external binding is copied from immutable Git publications. The original
review body is unchanged, with its PACK data lookup redirected to these exact
frozen JSONs. The caller rejects scripts in this data directory, disabling the
old pack-prefix own-control exception as new execution authority.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import time

HERE = Path(__file__).resolve().parent
DATA = HERE / 'legacy_authority_evidence'
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')
FW_REPO = Path('/workspace/repos/accel-sim-framework')
AA5 = '2d740ece2f5dbb6d99040a64f421e940687a48fa'
AA5_PACK = 'docs/dtc_l1/review_packs/DTC_LANE_AA5_GAUSSIAN_V1'
CONT = 'continuations/USER_RECHECK_20261018T030133Z/AUTHORITY_AND_FLOCK_AUDIT.json'

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def blob(repo, commit, path):
    if repo != FW_REPO or commit != AA5 or path != AA5_PACK + '/' + CONT:
        raise ValueError('UNREGISTERED_LEGACY_HISTORY_READ')
    return (DATA / 'AA5_AUTHORITY_AND_FLOCK_AUDIT.json').read_bytes()

def _selected(path, names, constants):
    tree = ast.parse(path.read_text(), filename=str(path))
    selected = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            selected.append(node)
        elif isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id in constants for t in node.targets):
            selected.append(node)
    found = {node.name for node in selected if isinstance(node, ast.FunctionDef)}
    if found != set(names):
        raise ValueError('FROZEN_PROCEDURE_CLOSURE_MISSING')
    return compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec')

def bind_frozen_procedures():
    bindings = json.loads((DATA / 'SOURCE_BINDINGS.json').read_text())
    for name, binding in bindings.items():
        if sha(DATA / name) != binding['sha256']:
            raise ValueError('FROZEN_LEGACY_SOURCE_CHANGED:' + name)
    scope = dict(globals(), PACK=DATA)
    exec(_selected(DATA / 'frozen_audit_site.py.txt', ['proc', 'snapshot'],
                   ['PAGE', 'AA5_PIDS', 'OLD_DISPATCHER']), scope)
    exec(_selected(DATA / 'frozen_review_authority.py.txt', ['review'], ['OLD', 'CONT']), scope)
    return scope['proc'], scope['snapshot'], scope['review']

def exact_legacy_output_sources():
    """Keep audited output helper path+SHA, never only its basename."""
    history = json.loads(blob(FW_REPO, AA5, AA5_PACK + '/' + CONT))
    return {str(Path(row['path']).resolve()): row['sha256'] for row in history['source_review']}
