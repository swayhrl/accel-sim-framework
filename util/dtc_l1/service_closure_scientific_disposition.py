"""Scientific overlays; never change terminal validation or immutable inputs."""

AUTHORIZATION = '5248a5ed482156450a3baa2799f26ebae02e1d93'
FORMAT_PENDING = frozenset({'Btree', '2DConvolution', 'LUD'})


def disposition(workload):
    if workload in FORMAT_PENDING:
        return 'FORMAT_APPLICABILITY_REVIEW_PENDING'
    if workload == 'Hotspot1':
        return 'HOLD_SHARED_TRACE_INTERPRETATION'
    return 'TERMINAL_SCOPE_ONLY_UNTIL_COMPARISON_COMPLETE'
