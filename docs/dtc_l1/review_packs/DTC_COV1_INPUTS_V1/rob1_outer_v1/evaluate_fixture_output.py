"""PREPARED_NOT_EXECUTED. Pure actual-LDST protocol classifier; no CLI."""
import re

CASES = ('omitted', 'explicit_zero', 'quota_one', 'bad_width', 'bad_mode', 'nonfinite')
ARGS = (('omitted','3','1'), ('0','3','1'), ('1','3','1'),
        ('2','3','1'), ('1','2','1'), ('1','3','0'))
MAX_STREAM = 512 * 1024


def classify(case, returncode, stdout, stderr, *, execution_failure_reason=None):
    """Protocol only; caller authenticates ABI/Popen/R2/cleanup independently."""
    def reject(reason):
        return dict(status='REJECT', case=case, reason=reason,
                    global_authority=False, whole_binary_OFF_equivalence=False)
    if case not in CASES:
        return reject('UNREGISTERED_CASE')
    if execution_failure_reason is not None:
        return reject('EXECUTION_RESOURCE_IDENTITY_OR_CLEANUP_FAILURE_OVERRIDES_EXIT')
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        return reject('RAW_BYTES_REQUIRED')
    if max(len(stdout), len(stderr)) > MAX_STREAM:
        return reject('PER_STREAM_BOUND')
    try:
        out, err = stdout.decode('utf-8'), stderr.decode('utf-8')
    except UnicodeDecodeError:
        return reject('INVALID_UTF8')
    lines = out.splitlines()
    records = [line for line in lines if line.startswith('ROB1_')]
    fatal = ('SIGSEGV', 'Assertion ', 'Assertion\n', 'assertion failed',
             'AddressSanitizer', 'UndefinedBehaviorSanitizer', 'terminate called')
    if any(word in out or word in err for word in fatal):
        return reject('UNEXPECTED_FATAL_DIAGNOSTIC')
    if case in CASES[:3]:
        width, done, retire = (1,14,16) if case == 'quota_one' else (4,12,14)
        expected = ('ROB1_COLLECTION_TRACE width=%d ready=11 start=12 done=%d retire=%d '
            'sectors=3 wb_denied=1 ref_final=0 ledger_closed=1 kernels=0 '
            'gpu_cycle_calls=0 threads_started=0') % (width,done,retire)
        if returncode != 0 or records != [expected] or err.strip():
            return reject('EXACT_ACTUAL_LDST_COMPLETION_PROTOCOL_REQUIRED')
        return dict(status='PASS_ACTUAL_LDST_COMPONENT_COMPLETION', case=case,
            collector_width=width, ready=11, collect_start=12, collect_done=done,
            retire=retire, requested_sectors=3, accepted_return_sectors=4,
            real_RF_bank_WB_denial=1, final_Ref=0, ledger_dependency_closed=1,
            scope='source assertions in matching assertion-enabled actual LDST fixture',
            modeled_kernels=0, GPU_cycle_calls=0, whole_binary_OFF_equivalence=False)
    # gpgpu_sim's installed SIGABRT handler prints this signature then _exit(1).
    # A raw -SIGABRT, unrelated nonzero, assertion or SIGSEGV is not equivalent.
    err_lines = err.splitlines()
    marker = 'DTC_COLLECTION_QUOTA_UNSUPPORTED_STOP'
    crash = '=== CRASH: SIGABRT (signal 6) ==='
    if returncode != 1 or records or out.count(marker) or err_lines.count(marker) != 1:
        return reject('EXACT_CTOR_QUOTA_REJECTION_REQUIRED')
    if err_lines.count(crash) != 1 or err_lines.count('Backtrace:') != 1 or err_lines.count('=== END BACKTRACE ===') != 1:
        return reject('EXACT_CORE_SIGABRT_HANDLER_REQUIRED')
    first, last = err_lines.index('Backtrace:'), err_lines.index('=== END BACKTRACE ===')
    if not (err_lines.index(marker) < err_lines.index(crash) < first < last):
        return reject('CTOR_CRASH_SIGNATURE_ORDER')
    frames=err_lines[first+1:last]
    if not frames or not all(re.search(r'\[0x[0-9a-fA-F]+\]$', row) for row in frames):
        return reject('REAL_BACKTRACE_RECORD_REQUIRED')
    outside=err_lines[:first]+err_lines[last:]
    if any(row not in ('',marker,crash,'Backtrace:','=== END BACKTRACE ===') for row in outside):
        return reject('UNEXPECTED_STDERR_OUTSIDE_CORE_ABORT_SIGNATURE')
    return dict(status='PASS_EXPECTED_ACTUAL_CTOR_REJECTION', case=case,
        actual_exit=1, abort_handler='SIGABRT_THEN__exit1',
        rejection='DTC_COLLECTION_QUOTA_UNSUPPORTED_STOP',
        completion_or_Ref_retirement_reached=False,
        per_negative_loaded_library_observation='UNAVAILABLE_UNLESS_SEPARATELY_OBSERVED',
        whole_binary_OFF_equivalence=False, global_authority=False)
