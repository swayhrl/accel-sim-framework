#!/usr/bin/env python3
"""CPU-only, synthetic FP64 algebra checks; no GPU or performance claims.

Toy model: H = W[input_ids] @ R; logits = H @ W.T, with one tied W.
Compare materialized total-gradient AdamW with delayed, row-tiled head-gradient
recomputation after the lookup gradient is ready. This is NOT a CCE/GPU kernel,
not a training-recipe qualification, and not a peak-memory benchmark.
Run: python cpu_semantic_checks.py --output CPU_CHECK_RESULTS.json
Dependency: NumPy. No network, PyTorch, CUDA, or model files required.
"""
from __future__ import annotations
import argparse
import json
import platform
from pathlib import Path
import numpy as np

BETA1, BETA2, LR, WD, EPS, STEP = 0.9, 0.98, 0.01, 0.02, 1e-8, 9
ATOL = RTOL = 1e-12  # Only this FP64 unit-test contract; never a GPU tolerance.


def forward(w, r, ids, labels):
    h = w[ids] @ r
    logits = h @ w.T
    maximum = logits.max(axis=1)
    lse = maximum + np.log(np.exp(logits - maximum[:, None]).sum(axis=1))
    valid = labels >= 0
    if not valid.any():
        raise ValueError('All-ignore mean-loss semantics intentionally out of scope')
    loss = float(np.mean(lse[valid] - logits[np.where(valid)[0], labels[valid]]))
    return h, lse, loss


def dz_tile(h, w_tile, lse, labels, lo):
    z = np.exp(h @ w_tile.T - lse[:, None])
    valid = labels >= 0
    local = labels - lo
    target_here = valid & (local >= 0) & (local < len(w_tile))
    row = np.where(target_here)[0]
    z[row, local[row]] -= 1.0
    z[~valid] = 0.0
    return z / int(valid.sum())


def adamw(w, m, v, grad, step=STEP):
    m_next = BETA1 * m + (1 - BETA1) * grad
    v_next = BETA2 * v + (1 - BETA2) * grad * grad
    update = (m_next / (1 - BETA1**step)) / (
        np.sqrt(v_next / (1 - BETA2**step)) + EPS
    )
    return w * (1 - LR * WD) - LR * update, m_next, v_next


def reference(w, r, ids, labels, m, v):
    h, lse, loss = forward(w, r, ids, labels)
    dz = dz_tile(h, w, lse, labels, 0)
    dh = dz @ w
    head = dz.T @ h
    lookup = np.zeros_like(w)
    np.add.at(lookup, ids, dh @ r.T)
    total = head + lookup
    return {
        'h': h, 'lse': lse, 'loss': loss, 'dh': dh,
        'head': head, 'lookup': lookup, 'grad': total,
        'state': adamw(w, m, v, total),
    }


def delayed_row_tiled(w0, r, ids, labels, m0, v0, tile, ref):
    # Copies isolate the two test arms, not proposed GPU working buffers.
    w, m, v = w0.copy(), m0.copy(), v0.copy()
    h, lse, loss = forward(w, r, ids, labels)
    dh = np.zeros_like(h)
    # All dH consumers read OLD W, before any coordinate is overwritten.
    for lo in range(0, len(w), tile):
        hi = min(lo + tile, len(w))
        dh += dz_tile(h, w[lo:hi], lse, labels, lo) @ w[lo:hi]
    lookup_upstream = dh @ r.T
    unique_ids, inverse = np.unique(ids, return_inverse=True)
    compact = np.zeros((len(unique_ids), w.shape[1]), dtype=np.float64)
    np.add.at(compact, inverse, lookup_upstream)
    # Real-model implementation must also prove every other old-W reader,
    # including checkpoint recomputation, has finished at this boundary.
    max_grad_error = 0.0
    for lo in range(0, len(w), tile):
        hi = min(lo + tile, len(w))
        # This tile still contains old weights. Use SAVED original LSE and H;
        # do not recompute normalization across already-updated vocabulary rows.
        grad = dz_tile(h, w[lo:hi], lse, labels, lo).T @ h
        selected = (unique_ids >= lo) & (unique_ids < hi)
        grad[unique_ids[selected] - lo] += compact[selected]
        max_grad_error = max(max_grad_error, float(np.max(abs(grad-ref['grad'][lo:hi]))))
        w[lo:hi], m[lo:hi], v[lo:hi] = adamw(w[lo:hi], m[lo:hi], v[lo:hi], grad)
    return (w, m, v), dh, loss, max_grad_error, len(unique_ids)


def max_error(left, right):
    return float(np.max(np.abs(left - right)))


def check_one(seed, shape, tile, ignore_some):
    vocab, hidden, tokens = shape
    rng = np.random.default_rng(seed)
    w = rng.normal(0, .2, (vocab, hidden))
    r = rng.normal(0, .3, (hidden, hidden))
    # Force repeated IDs and untouched input rows, with valid token IDs.
    ids = rng.integers(0, min(vocab-1, max(2, tokens//2)), tokens)
    ids[:2] = 1
    labels = rng.integers(0, vocab, tokens)
    if ignore_some:
        labels[::3] = -1
    m = rng.normal(0, .01, w.shape)
    v = rng.uniform(.01, .05, w.shape)
    ref = reference(w, r, ids, labels, m, v)
    got, dh, loss, grad_error, unique = delayed_row_tiled(w, r, ids, labels, m, v, tile, ref)
    errors = {'grad': grad_error, 'dh': max_error(dh,ref['dh']), 'loss':abs(loss-ref['loss'])}
    for name, a, b in zip(('w','m','v'), got, ref['state']):
        np.testing.assert_allclose(a,b,rtol=RTOL,atol=ATOL)
        errors[name] = max_error(a,b)
    np.testing.assert_allclose(dh,ref['dh'],rtol=RTOL,atol=ATOL)
    if grad_error > ATOL:
        raise AssertionError(f'Gradient error {grad_error} exceeds FP64 absolute contract')
    errors['next_forward_loss'] = abs(forward(got[0],r,ids,labels)[2] - forward(ref['state'][0],r,ids,labels)[2])
    if errors['next_forward_loss'] > ATOL:
        raise AssertionError('Next-forward loss mismatch')
    return {'seed':seed,'shape':list(shape),'row_tile':tile,'some_labels_ignored':ignore_some,
            'unique_lookup_rows':unique,'errors':errors,'pass':True}, (w,r,ids,labels,m,v,ref)


def finite_difference(case):
    w,r,ids,labels,_,_,ref = case
    numeric = np.zeros_like(w)
    delta = 1e-5
    for i in range(w.shape[0]):
        for j in range(w.shape[1]):
            plus, minus = w.copy(), w.copy()
            plus[i,j] += delta
            minus[i,j] -= delta
            numeric[i,j] = (forward(plus,r,ids,labels)[2]-forward(minus,r,ids,labels)[2])/(2*delta)
    error = max_error(numeric,ref['grad'])
    if error >= 2e-9:
        raise AssertionError(f'Finite-difference chain-rule error {error}')
    return {'parameters_checked':int(w.size),'delta':delta,'max_absolute_error':error,'pass':True}


def negative_controls(case):
    w,r,ids,labels,m,v,ref = case
    head_updated = adamw(w,m,v,ref['head'])
    # Wrong: update on one contribution, then do a second optimizer step.
    double_step = adamw(*head_updated,ref['lookup'],step=STEP+1)
    # Wrong: overwrite W before the dH branch has consumed old W.
    dz = dz_tile(ref['h'],w,ref['lse'],labels,0)
    early_dh = dz @ head_updated[0]
    # Wrong: clip each branch instead of clipping their sum.
    clip_limit = .003
    def clip(g):
        return g * min(1.0,clip_limit / max(float(np.linalg.norm(g)),1e-30))
    controls = {
        'two_separate_adamw_steps_weight_error':max_error(double_step[0],ref['state'][0]),
        'overwrite_before_dh_error':max_error(early_dh,ref['dh']),
        'clip_branches_before_sum_gradient_error':max_error(clip(ref['head'])+clip(ref['lookup']),clip(ref['grad'])),
    }
    if not all(x > 1e-8 for x in controls.values()):
        raise AssertionError(f'Negative control did not detect a change: {controls}')
    return {'errors':controls,'all_wrong_schedules_detected':True}


def joint_histogram_example():
    # Two DIFFERENT synthetic route workloads. Equal marginals do not imply
    # equal joint grouping. Not a semantically equivalent optimization pair.
    experts = adapters = 4
    aligned = np.zeros((experts,adapters),dtype=int)
    dispersed = np.zeros_like(aligned)
    for a in range(adapters):
        for token in range(8):
            aligned[[a,(a+1)%experts],a] += 1
            e = token % experts
            dispersed[[e,(e+1)%experts],a] += 1
    assert np.array_equal(aligned.sum(0),dispersed.sum(0))
    assert np.array_equal(aligned.sum(1),dispersed.sum(1))
    block_m = 16
    return {'label':'SYNTHETIC_STRUCTURE_ONLY_NOT_NOVELTY_OR_PERFORMANCE',
            'assignments':int(aligned.sum()),'block_m':block_m,
            'same_expert_and_adapter_marginals':True,
            'aligned_joint_counts':aligned.tolist(),'dispersed_joint_counts':dispersed.tolist(),
            'aligned_padded_slots':int((((aligned+block_m-1)//block_m)*block_m).sum()),
            'dispersed_padded_slots':int((((dispersed+block_m-1)//block_m)*block_m).sum())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('CPU_CHECK_RESULTS.json'))
    args=parser.parse_args()
    rows=[]
    first=None
    for seed in (0,1,2,3):
        for shape in ((13,5,7),(17,7,11)):
            for tile in (1,3,shape[0]):
                for ignore in (False,True):
                    row,case=check_one(seed,shape,tile,ignore)
                    rows.append(row)
                    if first is None:
                        first=case
    vocab,hidden,tokens=151936,896,2048
    result={
        'scope':'CHATGPT_CONTAINER_CPU_SYNTHETIC_FP64_UNIT_TEST_ONLY',
        'cuda_runs':0,'node109_runs':0,'node174_runs':0,'timings_measured':False,
        'python':platform.python_version(),'numpy':np.__version__,
        'tolerance':{'atol':ATOL,'rtol':RTOL,'scope':'FP64 toy only; not a GPU numeric contract'},
        'positive_case_count':len(rows),'positive_pass_count':sum(x['pass'] for x in rows),
        'max_errors':{k:max(x['errors'][k] for x in rows) for k in rows[0]['errors']},
        'finite_difference':finite_difference(first),'negative_controls':negative_controls(first),
        'shape_only_byte_accounting':{
            'vocab':vocab,'hidden':hidden,'illustrative_tokens':tokens,
            'weight_elements':vocab*hidden,
            'one_bf16_dense_gradient_MiB':vocab*hidden*2/(1024**2),
            'one_fp32_dense_gradient_MiB':vocab*hidden*4/(1024**2),
            'saved_bf16_final_hidden_MiB':tokens*hidden*2/(1024**2),
            'fp32_compact_lookup_gradient_upper_MiB':tokens*hidden*4/(1024**2),
            'fp32_lse_MiB':tokens*4/(1024**2),
            'not_measured_peak_memory_saving':True},
        'joint_histogram_example':joint_histogram_example(),
        'limitations':['No checkpoint/model state or GPU implementation is qualified.',
                       'FP64 toy is neither BF16 bitwise equivalence nor training-quality evidence.',
                       'No global clipping, gradient scaling, accumulation, distributed reduction, dropout/recompute recipe support.',
                       'The toy forward materializes logits; this is an algebra test, not an efficient CE implementation.',
                       'No runtime, cache, traffic, occupancy or actual peak-memory measurements.'],
        'cases':rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('positive_case_count','positive_pass_count','max_errors','finite_difference','negative_controls','shape_only_byte_accounting','joint_histogram_example')},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
