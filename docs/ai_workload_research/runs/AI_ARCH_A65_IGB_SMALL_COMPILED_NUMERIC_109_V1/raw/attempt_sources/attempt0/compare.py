"""CPU observer only; original allclose direction and tolerances are explicit."""
import numpy as np


def identity(left, right):
    ln = list(left)
    rn = list(right)
    return {'count_match': len(ln) == len(rn), 'ordered_names_match': ln == rn,
            'names_left_only': sorted(set(ln) - set(rn)),
            'names_right_only': sorted(set(rn) - set(ln)),
            'per_name': {n: {'shape_match': left[n].shape == right[n].shape,
                             'dtype_match': left[n].dtype == right[n].dtype}
                         for n in ln if n in right}}


def stats(reference, candidate, atol, rtol):
    assert reference.shape == candidate.shape and reference.dtype == candidate.dtype
    a = reference.astype(np.float64)
    b = candidate.astype(np.float64)
    finite = np.isfinite(a) & np.isfinite(b)
    delta = np.abs(a - b)
    # Matches torch.allclose(A, B): B supplies the relative-tolerance denominator.
    tolerance = atol + rtol * np.abs(b)
    bad = ~finite | (delta > tolerance)
    idx = np.flatnonzero(bad)[:8]
    finite_delta = delta[finite]
    ratio = delta[finite] / tolerance[finite]
    rel = delta[finite] / np.maximum(np.abs(a[finite]), 1e-12)
    coords = []
    for flat in idx:
        point = np.unravel_index(int(flat), a.shape)
        coords.append({'coordinate': [int(x) for x in point],
                       'reference': float(a[point]) if np.isfinite(a[point]) else str(a[point]),
                       'candidate': float(b[point]) if np.isfinite(b[point]) else str(b[point]),
                       'reference_abs': float(abs(a[point])) if np.isfinite(a[point]) else None,
                       'tolerance': float(tolerance[point]) if np.isfinite(tolerance[point]) else None})
    return {'pass': not bool(bad.any()), 'elements': int(a.size),
            'max_abs': float(finite_delta.max()) if finite_delta.size else None,
            'max_abs_over_tolerance': float(ratio.max()) if ratio.size else None,
            'normalized_remaining_margin': float(1 - ratio.max()) if ratio.size else None,
            'max_rel_reference_floor_1e_12': float(rel.max()) if rel.size else None,
            'nonfinite_reference': int((~np.isfinite(a)).sum()),
            'nonfinite_candidate': int((~np.isfinite(b)).sum()),
            'different_elements_exact': int((a != b).sum()),
            'failed_elements': int(bad.sum()), 'first_failures': coords,
            'atol': atol, 'rtol': rtol,
            'gate_denominator': 'atol + rtol*abs(candidate), original torch.allclose(A,B)',
            'diagnostic_relative_denominator': 'max(abs(reference),1e-12); does not alter gate'}


def parameter_pairs(left, right, atol, rtol):
    meta = identity(left, right)
    matching = meta['ordered_names_match'] and meta['count_match'] and all(
        x['shape_match'] and x['dtype_match'] for x in meta['per_name'].values())
    rows = {n: stats(left[n], right[n], atol, rtol) for n in left
            if n in right and left[n].shape == right[n].shape and left[n].dtype == right[n].dtype}
    return {'identity': meta, 'identity_pass': matching,
            'numerical_pass': matching and all(x['pass'] for x in rows.values()),
            'parameters': rows}


def classify(ab, ac, initial_and_input_pass=True):
    if not initial_and_input_pass or not ab['identity_pass'] or not ac['identity_pass']:
        return 'COMPARATOR_OR_IDENTITY_DEFECT'
    if not ab['numerical_pass']:
        return 'EAGER_EAGER_NUMERIC_VARIABILITY'
    if not ac['numerical_pass']:
        return 'COMPILED_PATH_NUMERIC_NONALIGNMENT'
    return 'SAME_BATCH_NUMERIC_CONTROL_PASS'
