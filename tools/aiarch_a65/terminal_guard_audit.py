"""CPU-only audit of a terminal NVML/process-list race; no GPU query or rerun."""
import json
from paths import R, save


def main():
    ledger = json.loads((R / 'gpu_ledger.json').read_text())
    attempt = ledger['attempts'][-1]
    child = attempt['owned_child_pid']
    # Directed source example only, NOT a reconstruction of uncaptured actual PIDs.
    before_exit_snapshot = [(child, 6858)]
    after_exit_group = []
    old = any(pid not in after_exit_group for pid, _ in before_exit_snapshot)
    proposed = any(pid != child and pid not in after_exit_group for pid, _ in before_exit_snapshot)
    actual_foreign_example = any(pid != child and pid not in after_exit_group for pid, _ in [(child + 1, 1)])
    assert old and not proposed and actual_foreign_example
    save('terminal_supervisor_guard_audit.json', {
        'observed_flag': attempt['reason'], 'child_returncode': attempt['child_returncode'],
        'last_samples': attempt['samples'][-3:],
        'NVML_after_owned_exit': attempt['NVML_apps_after_owned_exit'],
        'actual_PID_list_at_flag': 'NOT_CAPTURED_BY_EXECUTED_SUPERVISOR',
        'conclusion': 'terminal foreign-task flag is preserved and unresolved; must not claim full exclusivity PASS',
        'hypothesis': 'apps snapshot may contain own child just before exit while subsequent group snapshot is empty',
        'CPU_directed_predicate_reproduction': 'PASS: false-positive possible for own-child exit; proposed explicit-child exclusion retains foreign-PID detection',
        'reproduction_is_actual_GPU_evidence': False,
        'GPU_operations_or_retries': 0,
        'executed_GPU_source_modified': False,
        'next_required_wrapper_change': 'record NVML PID snapshot and group PID snapshot atomically enough for audit; always retain known owned-child identity across exit',
        'no_extra_GPU_run_because_numeric_gate_already_failed': True})
    print('CPU_TERMINAL_GUARD_AUDIT_PRESERVED_UNRESOLVED_FLAG')


if __name__ == '__main__':
    main()
