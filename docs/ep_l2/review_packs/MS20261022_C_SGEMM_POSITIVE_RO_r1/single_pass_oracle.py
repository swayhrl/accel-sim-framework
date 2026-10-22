#!/usr/bin/env python3
"""I/O-only adapter for the frozen C oracle; no classifier/epoch changes.

Exactly one body open supplies original stream_kernel and a byte SHA together.
The old pre-hash call returns the declared EXPECTATION, never a measured hash;
the old post-hash call requires completed streaming and an exact measured match.
No native/simulator/build entry, full-body verify(), or retry is called.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import time


def load_oracle(root):
    path = root / 'util/ep_l2/mechanism_study_c/ro_oracle.py'
    spec = importlib.util.spec_from_file_location('frozen_ro_oracle_single_pass', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def run(command, body, expected, output, producer, expected_records=None):
    root = Path(__file__).resolve().parents[4]
    oracle, source = load_oracle(root)
    source_bytes = source.read_bytes()
    frozen = subprocess.check_output(['git', '-C', str(root), 'show', producer + ':' + str(source.relative_to(root))])
    if source_bytes != frozen:
        raise ValueError('oracle source not byte-identical to published producer')
    adapter = Path(__file__).resolve()
    if adapter.read_bytes() != subprocess.check_output(['git', '-C', str(root), 'show', producer + ':' + str(adapter.relative_to(root))]):
        raise ValueError('single-pass adapter must be published before real-input use')
    return classify(oracle, command, body, expected, output, producer, expected_records,
                    dict(path=str(source), sha256=hashlib.sha256(source_bytes).hexdigest(),
                         source_commit=producer), adapter)


def classify(oracle, command, body, expected, output, producer, expected_records=None,
             source_identity=None, adapter=None):
    command, body, output = Path(command).resolve(), Path(body).resolve(), Path(output)
    before = body.stat()
    body_stamp = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    digest = hashlib.sha256()
    state = dict(body_opens=0, body_hash_requests=0, bytes_read=0,
                 complete=False, instruction_records=0)
    real_sha, real_stream = oracle.sha256, oracle.stream_kernel
    began = time.monotonic()
    last_report = began

    @contextlib.contextmanager
    def one_open(path):
        nonlocal last_report
        if Path(path).resolve() != body or state['body_opens']:
            raise ValueError('one exact body open only; no second input/scan')
        state['body_opens'] += 1
        with body.open('rb', buffering=1024 * 1024) as stream:
            def lines():
                nonlocal last_report
                for raw in stream:
                    digest.update(raw)
                    state['bytes_read'] += len(raw)
                    now = time.monotonic()
                    if now - last_report >= 30:
                        print(json.dumps(dict(progress_bytes=state['bytes_read'],
                                              expected_bytes=before.st_size,
                                              instruction_records=state['instruction_records'],
                                              elapsed_seconds=now-began)), flush=True)
                        last_report = now
                    yield raw.decode('utf-8')
                state['complete'] = True
            yield lines()
        after = body.stat()
        if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != body_stamp:
            raise ValueError('body stat identity changed during single pass')
        if not state['complete'] or state['bytes_read'] != before.st_size:
            raise ValueError('body not completely consumed')
        if digest.hexdigest() != expected:
            raise ValueError('measured single-pass body SHA differs from frozen input')

    def bound_sha(path):
        if Path(path).resolve() != body:
            return real_sha(path)
        state['body_hash_requests'] += 1
        if state['body_hash_requests'] == 1 and state['body_opens'] == 0:
            return expected  # declared precondition; not a fresh observation
        if state['body_hash_requests'] == 2 and state['complete'] and digest.hexdigest() == expected:
            return digest.hexdigest()
        raise ValueError('unexpected trace hash request; a second read is forbidden')

    def counted_stream(path):
        for event in real_stream(path):
            state['instruction_records'] += 1
            yield event
        if expected_records is not None and state['instruction_records'] != expected_records:
            raise ValueError('complete parser instruction-record count mismatch')

    oracle.open_trace, oracle.sha256, oracle.stream_kernel = one_open, bound_sha, counted_stream
    manifest = oracle.build(command, output, oracle.SCOPE, producer)
    if state['body_opens'] != 1 or state['body_hash_requests'] != 2 or not state['complete']:
        raise ValueError('single-pass identity contract did not close')
    # Additional denominators read the completed line DB; never reread trace.
    db = sqlite3.connect('file:' + str(output / 'oracle.sqlite3') + '?mode=ro', uri=True)
    sql = db.execute('SELECT count(*),sum(reads>0),coalesce(sum(reads),0),coalesce(sum(writes),0),coalesce(sum(atomics),0) FROM lines').fetchone()
    db.close()
    metrics = dict(schema='C_SINGLE_PASS_ORACLE_RECEIPT_V1',
                   status='PASS_COMPLETE_ORACLE_MODEL_ONLY_NOT_E_QUALIFIED',
                   preparation_status='PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED',
                   producer_commit=producer, source_identity=source_identity,
                   adapter_sha256=hashlib.sha256(adapter.read_bytes()).hexdigest() if adapter else None,
                   exact_input_sha256=digest.hexdigest(), input_stat_before=list(body_stamp),
                   commandlist_sha256=real_sha(command), **state,
                   declared_pre_hash='Frozen expected value only; completed streaming SHA independently compared before post-hash/manifest completion',
                   complete_source_parser='Original stream_kernel/instruction/memory_kind/build line classification unchanged; adapter only supplies raw byte iterator, I/O binding and observation counts',
                   unique_global_lines=sql[0], read_containing_global_lines=sql[1],
                   global_read_lane_line_references=sql[2], global_write_lane_line_references=sql[3],
                   global_atomic_lane_line_references=sql[4],
                   elapsed_seconds=time.monotonic()-began,
                   self_maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                   native_or_simulator_or_build_invocations=0)
    (output / 'SINGLE_PASS_RECEIPT.json').write_text(json.dumps(metrics, indent=2)+'\n')
    print(json.dumps(metrics), flush=True)
    return manifest, metrics


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commandlist', required=True)
    parser.add_argument('--body', required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--producer', required=True)
    parser.add_argument('--expected-records', type=int, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256*2**20, 256*2**20))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    allowed = sorted(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {allowed[0]})
    run(args.commandlist, args.body, args.expected_sha256, Path(args.output),
        args.producer, args.expected_records)
