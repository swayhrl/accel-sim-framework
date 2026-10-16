"""CPU-only directed observer tests, without importing Torch or initializing CUDA."""
import numpy as np
from compare import stats, parameter_pairs, classify


def main():
    a = {'p': np.array([0., 1., -1.], dtype=np.float32)}
    good = parameter_pairs(a, a, 1e-6, 1e-4)
    assert good['numerical_pass']
    near_zero = {'p': np.array([2e-6, 1., -1.], dtype=np.float32)}
    bad = parameter_pairs(a, near_zero, 1e-6, 1e-4)
    assert not bad['numerical_pass']
    assert bad['parameters']['p']['failed_elements'] == 1
    assert bad['parameters']['p']['first_failures'][0]['coordinate'] == [0]
    renamed = parameter_pairs(a, {'q': a['p']}, 1e-6, 1e-4)
    assert not renamed['identity_pass']
    truncated = parameter_pairs({**a, 'q': a['p']}, a, 1e-6, 1e-4)
    assert not truncated['identity_pass']
    wrong_shape = parameter_pairs(a, {'p': a['p'].reshape(1, 3)}, 1e-6, 1e-4)
    assert not wrong_shape['identity_pass']
    wrong_dtype = parameter_pairs(a, {'p': a['p'].astype(np.float64)}, 1e-6, 1e-4)
    assert not wrong_dtype['identity_pass']
    nan = stats(np.array([np.nan], dtype=np.float32), np.array([np.nan], dtype=np.float32), 1e-6, 1e-4)
    assert not nan['pass'] and nan['nonfinite_candidate'] == 1
    assert classify(good, good) == 'SAME_BATCH_NUMERIC_CONTROL_PASS'
    assert classify(bad, bad) == 'EAGER_EAGER_NUMERIC_VARIABILITY'
    assert classify(good, bad) == 'COMPILED_PATH_NUMERIC_NONALIGNMENT'
    assert classify(renamed, good) == 'COMPARATOR_OR_IDENTITY_DEFECT'
    # Check B-denominator explicitly rather than silently reversing allclose.
    t = stats(np.array([1.], dtype=np.float32), np.array([2.], dtype=np.float32), 0, .6)
    assert t['pass']
    print('PASS_12_DIRECTED_COMPARATOR_CASES_NO_TORCH')


if __name__ == '__main__':
    main()
