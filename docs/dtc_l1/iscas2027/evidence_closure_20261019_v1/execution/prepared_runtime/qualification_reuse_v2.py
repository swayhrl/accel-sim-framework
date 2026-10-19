"""Read-only exact-source reuse of already executed CPU cases, never a test.

Old resource decisions remain old decisions. A new entry still needs its own
fresh admission. This joins published actual receipts to unchanged observer /
wait-dispatch code, with only the user's explicit disk-only guard addition.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALGORITHMS = ('test_shared_authority.py', 'shared_authority.py',
              'legacy_authority_runtime.py', 'vendor/ownership.py',
              'vendor/mapping_roles.py', 'vendor/oom_watchdog.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load(descriptor):
    path = Path(descriptor['path'])
    require(sha(path) == descriptor['sha256'], 'PUBLISHED_REUSE_EVIDENCE_CHANGED')
    return json.loads(path.read_text())


def witness(registration):
    spec = registration['qualified_source_reuse']
    proof = load(spec)
    require(proof['status'] == 'EXACT_EXECUTED_CPU_SOURCE_REUSE_WITH_USER_DISK_ONLY_DELTA',
            'CPU_REUSE_WITNESS_REQUIRED')
    require(proof['current_prepared_source_sha256'] == registration['prepared_source_sha256'],
            'CPU_REUSE_CURRENT_CLOSURE_CHANGED')
    previous = load(proof['old_shared_registration'])
    for relative in ALGORITHMS:
        require(previous['prepared_source_sha256'][relative] ==
                registration['prepared_source_sha256'][relative] == sha(HERE / relative),
                'EXECUTED_CPU_ALGORITHM_CHANGED:' + relative)
    # This is executable structural equality, not a boolean PASS declaration.
    # Remove exactly the source-authorized five-GiB check and shutil import;
    # all original fork/wait/ownership/maps/cleanup code must remain identical.
    old_source = Path(proof['old_guard_source']['path'])
    require(sha(old_source) == proof['old_guard_source']['sha256'], 'OLD_GUARD_SOURCE_CHANGED')
    old = ast.parse(old_source.read_text())
    current = ast.parse((HERE / 'vendor/guarded_process.py').read_text())
    removed = 0
    for node in ast.walk(current):
        if isinstance(node, ast.Import):
            node.names = [name for name in node.names if name.name != 'shutil']
        if isinstance(node, ast.FunctionDef) and node.name == 'periodic':
            for statement in list(node.body):
                if isinstance(statement, ast.If) and any(isinstance(child, ast.Constant) and
                    child.value == 'USER_DISK_FLOOR_AT_OR_BELOW_5GiB' for child in ast.walk(statement)):
                    require(ast.unparse(statement.test) ==
                        'instant - last_oom >= 0.25 and shutil.disk_usage(dest).free <= 5 * 1024 ** 3',
                        'DISK_ONLY_SOURCE_DELTA_CHANGED')
                    node.body.remove(statement)
                    removed += 1
    require(removed == 1 and ast.dump(old, include_attributes=False) ==
            ast.dump(current, include_attributes=False), 'ORIGINAL_GUARD_DISPATCH_OR_CLEANUP_CHANGED')
    old_qualifier = Path(proof['old_qualifier_source']['path'])
    require(sha(old_qualifier) == proof['old_qualifier_source']['sha256'],
            'ORIGINAL_EXECUTED_QUALIFIER_SOURCE_CHANGED')
    def generation_block(text):
        start = text.index(' for label,engine,kind in [')
        return text[start:text.index(' run_real_changed_interfaces(dest, manifests, env)', start)]
    require(generation_block(old_qualifier.read_text()) == generation_block(
        (HERE / 'qualify_ag5_changed_dispatch_v2.py').read_text()),
        'ORIGINAL_FIVE_GENERATION_CASES_CHANGED')
    return proof, spec['sha256']


def negative(registration):
    from cpu_admission_v2 import execution_binding, require_execution_binding
    proof, digest = witness(registration)
    receipt = load(proof['actual_negative_receipt'])
    old_spec = proof['old_shared_registration']
    previous = load(old_spec)
    require_execution_binding(receipt, execution_binding(old_spec['path'], previous))
    require(receipt['cases'] == 14 and receipt['returncode'] == 0 and
            receipt['test_source_sha256'] == sha(HERE / 'test_shared_authority.py'),
            'ACTUAL_FOURTEEN_EXECUTED_CASES_REQUIRED')
    return receipt, dict(status='REUSED_ACTUAL_FOURTEEN_UNCHANGED_ALGORITHM_CASES',
        source_reuse_witness_sha256=digest, new_cases_executed=0,
        prior_admission_relabelled=False, current_external_roles_still_need_actual_observation=True)


def generation(registration):
    from cpu_admission_v2 import execution_binding, require_execution_binding
    proof, digest = witness(registration)
    receipt = load(proof['actual_generation_receipt'])
    old_spec = proof['old_changed_registration']
    previous = load(old_spec)
    require_execution_binding(receipt, execution_binding(old_spec['path'], previous))
    require(len(receipt['cases']) == 5 and
            all(row['status'] == 'PASS_EXPECTED_RESULT' for row in receipt['cases']),
            'ACTUAL_FIVE_GENERATION_PASSES_REQUIRED')
    result = copy.deepcopy(receipt)
    result.update(execution_binding(HERE.parent / 'CPU_AG5_CHANGED_DISPATCH_REGISTRATION_V2.json', registration))
    result.update(status='PASS_REUSED_EXACT_GUARD_WAIT_DISPATCH_FIVE_CASES',
        source_reuse_witness_sha256=digest, new_generation_cases_executed=0,
        original_actual_receipt_sha256=proof['actual_generation_receipt']['sha256'],
        old_admission_relabelled=False)
    return result


def root_order(registration):
    proof, digest = witness(registration)
    rows = load(proof['actual_real_cases_receipt'])
    row = copy.deepcopy(rows[0])
    require(row['case'] == 'real_child_first_stop_after_parent_reaped' and row['passed'] is True and
            row['terminal']['status'] == 'PASS_GUARDED_NATURAL_EXIT0' and
            row['terminal']['owned_children_live'] == 0 and
            not row['terminal']['ownership']['pending'], 'ACTUAL_FIRST_ROOT_ORDER_PASS_REQUIRED')
    row.update(reused_actual_case=True, new_case_executed=False,
               source_reuse_witness_sha256=digest, old_admission_relabelled=False)
    return row
