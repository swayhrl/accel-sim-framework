"""One real frozen minibatch; three qualification updates only, no formal training."""
import os
assert os.environ.get('A65_GPU_LOCK_HELD') == '1', 'PARENT_SHARED_GPU_LOCK_REQUIRED'
import copy
import gc
import hashlib
import importlib.metadata
import json
import time
import traceback
import numpy as np
from paths import OLD, R, W, save, sha, event
from math_copy import (torch, dgl, gb, GraphSAGE, DataContext, train_step,
                       validate_mb, FEAT, LABEL, IP, IX, B, sync)
from compare import parameter_pairs, stats, classify


def stage(name, **kw):
    save('current_phase.json', {'phase': name, 'monotonic': time.monotonic(), **kw})
    event(name, **kw)
    assert time.monotonic() < float(os.environ['A65_GPU_DEADLINE']) - 15, 'GPU_TIME_MARGIN'


def digest(x):
    return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()


def cpu_parameters(model):
    return {n: p.detach().cpu().numpy().copy() for n, p in model.named_parameters()}


def state_identity(values):
    h = hashlib.sha256()
    rows = []
    for n, value in values.items():
        entry = {'name': n, 'dtype': str(value.dtype), 'shape': list(value.shape),
                 'sha256': digest(value)}
        h.update(json.dumps(entry, sort_keys=True).encode())
        rows.append(entry)
    return {'sha256': h.hexdigest(), 'parameters': rows}


def input_tensors(mb):
    out = {'seeds': mb.seeds, 'labels': mb.labels, 'input_nodes': mb.input_nodes,
           'features': mb.node_features['feat']}
    for i, sg in enumerate(mb.sampled_subgraphs):
        out[f'L{i}.indptr'] = sg.sampled_csc.indptr
        out[f'L{i}.indices'] = sg.sampled_csc.indices
        for name in ['original_row_node_ids', 'original_column_node_ids', 'original_edge_ids']:
            value = getattr(sg, name)
            if value is not None:
                assert isinstance(value, torch.Tensor)
                out[f'L{i}.{name}'] = value
    return out


def frozen_identity(mb):
    rows = {}
    for n, value in input_tensors(mb).items():
        assert value.is_contiguous()
        h = hashlib.sha256()
        flat = value.detach().view(-1)
        for off in range(0, flat.numel(), 4 * 1024**2):
            h.update(flat[off:off + 4 * 1024**2].cpu().numpy().tobytes())
        rows[n] = {'sha256': h.hexdigest(), 'shape': list(value.shape),
                   'dtype': str(value.dtype)}
    return {'sha256': hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
            'tensors': rows}


def freeze(actual):
    mb = copy.copy(actual)
    for name, value in vars(actual).items():
        if isinstance(value, torch.Tensor):
            setattr(mb, name, value.clone())
    mb.node_features = {n: x.clone() for n, x in actual.node_features.items()}
    mb.sampled_subgraphs = []
    for old in actual.sampled_subgraphs:
        sg = copy.copy(old)
        sg.sampled_csc = gb.CSCFormatBase(indptr=old.sampled_csc.indptr.clone(),
                                        indices=old.sampled_csc.indices.clone())
        for name, value in vars(old).items():
            if isinstance(value, torch.Tensor):
                setattr(sg, name, value.clone())
        mb.sampled_subgraphs.append(sg)
    return mb


def snapshot(tag, model, opt, loss):
    updated = cpu_parameters(model)
    np.savez_compressed(R / 'raw' / (tag + '_updated.npz'), **updated)
    gradients = {n: p.grad.detach().cpu().numpy().copy() for n, p in model.named_parameters() if p.grad is not None}
    missing_gradients = [n for n, p in model.named_parameters() if p.grad is None]
    np.savez_compressed(R / 'raw' / (tag + '_gradient.npz'), **gradients)
    buffers = []
    steps = {}
    for n, p in model.named_parameters():
        state = opt.state[p]
        steps[n] = float(state['step'].item()) if 'step' in state else 'MISSING'
        for key, v in state.items():
            assert isinstance(v, torch.Tensor)
            a = v.detach().cpu().numpy()
            buffers.append({'parameter': n, 'buffer': key, 'shape': list(a.shape),
                            'dtype': str(a.dtype), 'sha256': digest(a),
                            'storage_ptr': v.untyped_storage().data_ptr(), 'device': str(v.device)})
    out = {'tag': tag, 'loss': float(loss) if np.isfinite(loss) else str(loss),
           'parameter_identity': state_identity(updated),
           'gradient_identity': state_identity(gradients), 'optimizer_buffers': buffers,
           'nonfinite_updated': {n: int((~np.isfinite(a)).sum()) for n, a in updated.items()},
           'nonfinite_gradient': {n: int((~np.isfinite(a)).sum()) for n, a in gradients.items()},
           'nonzero_gradient_elements': {n: int(np.count_nonzero(a)) for n, a in gradients.items()},
           'optimizer_actual_steps_each_parameter': steps, 'missing_gradients': missing_gradients}
    save(tag + '_observation.json', out)
    assert not missing_gradients, 'MISSING_GRADIENTS_SEE_PARTIAL_RAW'
    assert all(x == 1 for x in steps.values()), 'EXACTLY_ONE_REAL_ADAM_STEP_PER_MODEL'
    assert np.isfinite(loss) and not any(out['nonfinite_updated'].values()) and not any(out['nonfinite_gradient'].values()), 'NONFINITE_OBSERVATION'
    assert sum(out['nonzero_gradient_elements'].values()) > 0, 'ALL_ZERO_GRADIENT'
    return updated, gradients, out


def authoritative_update_pair(values, models, candidate):
    pair = parameter_pairs(values['eagerA']['updated'], values[candidate]['updated'], 1e-6, 1e-4)
    left = dict(models['eagerA'].named_parameters())
    right = dict(models[candidate].named_parameters())
    assert list(left) == list(right)
    for name in left:
        a = left[name].detach()
        b = right[name].detach()
        decision = bool(torch.allclose(a, b, atol=1e-6, rtol=1e-4))
        bad = (~torch.isclose(a, b, atol=1e-6, rtol=1e-4)).cpu().numpy()
        assert decision == (not bool(bad.any()))
        row = pair['parameters'][name]
        row['CPU_float64_diagnostic_pass'] = row['pass']
        row['pass'] = decision
        row['failed_elements'] = int(bad.sum())
        failures = []
        for flat in np.flatnonzero(bad)[:8]:
            point = np.unravel_index(int(flat), bad.shape)
            av = float(values['eagerA']['updated'][name][point])
            bv = float(values[candidate]['updated'][name][point])
            failures.append({'coordinate': [int(x) for x in point],
                             'reference': av, 'candidate': bv,
                             'tolerance_float64_diagnostic': 1e-6 + 1e-4 * abs(bv)})
        row['first_failures'] = failures
        row['decision_authority'] = 'actual frozen Torch2.2 torch.allclose(A,B,atol1e-6,rtol1e-4); isclose failure mask'
    pair['numerical_pass'] = pair['identity_pass'] and all(x['pass'] for x in pair['parameters'].values())
    return pair


def main():
    stage('IMPORT_AND_DEVICE_QUALIFICATION')
    versions = {n: importlib.metadata.version(n) for n in ['torch', 'dgl', 'torch-geometric', 'numpy', 'triton']}
    assert versions == {'torch': '2.2.0+cu121', 'dgl': '2.4.0+cu121',
                        'torch-geometric': '2.6.1', 'numpy': '1.26.4', 'triton': '2.2.0'}
    assert '4080' in torch.cuda.get_device_name(0) and torch.cuda.get_device_capability(0) == (8, 9)
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.set_float32_matmul_precision('highest')
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.cuda.set_per_process_memory_fraction(.70, 0)
    torch._dynamo.config.cache_size_limit = 32
    save('device_and_software.json', {'versions': versions, 'device': torch.cuda.get_device_name(0),
                                     'torch_CUDA': torch.version.cuda, 'allocator_fraction': .70,
                                     'FP32': True, 'TF32': False, 'highest': True,
                                     'process_affinity': sorted(os.sched_getaffinity(0)),
                                     'Torch_threads': torch.get_num_threads(),
                                     'DataLoader_workers': 0})
    stage('UNIQUE_INITIAL_MODEL_STATE')
    torch.manual_seed(20261015)
    gb.seed(20261015)
    origin = GraphSAGE()
    initial = {n: x.detach().clone() for n, x in origin.state_dict().items()}
    initial_np = cpu_parameters(origin)
    np.savez_compressed(R / 'raw/initial_parameters.npz', **initial_np)
    identity = state_identity(initial_np)
    models = {}
    opts = {}
    initial_rows = []
    seen = set()
    for tag in ['eagerA', 'eagerB', 'compiledC']:
        model = GraphSAGE().cuda()
        model.load_state_dict(initial)
        opt = torch.optim.Adam(model.parameters(), lr=.003, weight_decay=0)
        actual = cpu_parameters(model)
        assert list(actual) == list(initial_np)
        assert all(np.array_equal(actual[n].view(np.uint32), initial_np[n].view(np.uint32)) for n in actual), 'INITIAL_MODEL_BITWISE_DIFFERENCE'
        current = [p.untyped_storage().data_ptr() for p in model.parameters()]
        assert len(set(current)) == len(current) and seen.isdisjoint(current), 'MUTABLE_PARAMETER_STORAGE_ALIAS'
        seen.update(current)
        assert opt.state_dict()['state'] == {}
        optim_json = json.dumps(opt.state_dict(), sort_keys=True)
        initial_rows.append({'tag': tag, 'model_identity': state_identity(actual),
                             'ordered_names': list(actual), 'storage_ptrs': current,
                             'model_object_id': id(model), 'optimizer_object_id': id(opt),
                             'optimizer_initial_state': opt.state_dict(),
                             'optimizer_initial_SHA256': hashlib.sha256(optim_json.encode()).hexdigest()})
        models[tag] = model
        opts[tag] = opt
    assert len({x['model_identity']['sha256'] for x in initial_rows}) == 1
    assert len({x['optimizer_initial_SHA256'] for x in initial_rows}) == 1
    save('initial_identities.json', {'status': 'PASS_BITWISE_INDEPENDENT', 'seed': 20261015,
                                     'reference_identity': identity, 'models': initial_rows,
                                     'mutable_optimizer_buffers_initially_empty': True})
    del origin, initial
    stage('ONE_NATURAL_PINNED_CACHE_ON_MINIBATCH')
    train = np.load(OLD / 'train_ids.npy', mmap_mode='r')
    item = gb.ItemSet((torch.from_numpy(np.array(train, copy=True)),
                       torch.from_numpy(np.asarray(LABEL[train], dtype=np.int64))), names=('seeds', 'labels'))
    natural = gb.ItemSampler(item, batch_size=B, shuffle=True, drop_last=True, seed=20261015)
    root_batch = next(iter(natural))
    ids = root_batch.seeds.numpy().copy()
    assert np.array_equal(ids, np.load(OLD / 'order_20261015.npy', mmap_mode='r')[:B]), 'NATURAL_ITEM_SAMPLER_ORDER_CHANGED'
    pinned = (torch.from_numpy(IP).pin_memory(), torch.from_numpy(IX).pin_memory(),
              torch.from_numpy(FEAT).pin_memory())
    ctx = DataContext('PINNED_CACHE_ON', pinned)
    gb.seed(20261015)
    loader = ctx.loader(ids)
    iterator = iter(loader)
    actual = next(iterator)
    sync()
    save('actual_minibatch_semantics.json', validate_mb(actual, 'A65_UNIQUE_NATURAL_BATCH'))
    mb = freeze(actual)
    sync()
    original_identity = frozen_identity(actual)
    frozen = frozen_identity(mb)
    assert original_identity == frozen, 'LOSSLESS_FREEZE_FAILED'
    try:
        next(iterator)
        raise AssertionError('MORE_THAN_ONE_SAMPLED_MINIBATCH')
    except StopIteration:
        pass
    del actual, iterator, loader, natural, root_batch, item
    gc.collect()
    tensors = input_tensors(mb)
    small = {n: x.detach().cpu().numpy().copy() for n, x in tensors.items() if n != 'features'}
    np.savez_compressed(R / 'raw/frozen_minibatch_arrays.npz', **small)
    global_ids = small['input_nodes']
    feature_hasher = hashlib.sha256()
    for off in range(0, len(global_ids), 4096):
        value = mb.node_features['feat'][off:off + 4096].detach().cpu().numpy()
        expected = np.asarray(FEAT[global_ids[off:off + 4096]])
        assert np.array_equal(value.view(np.uint32), expected.view(np.uint32)), 'FULL_FEATURE_FALLBACK_BYTES_MISMATCH'
        assert np.isfinite(value).all()
        feature_hasher.update(value.tobytes())
    assert feature_hasher.hexdigest() == frozen['tensors']['features']['sha256']
    assert ctx.cache is not None and ctx.cache.cache_size_in_bytes == 128 * 1024**2 and ctx.graph._gpu_graph_cache is not None
    save('frozen_input_identity.json', {'status': 'PASS_LOSSLESS_FULL_FEATURE_VERIFIED',
                                      'identity': frozen, 'input_nodes': len(global_ids),
                                      'cache': ctx.stats(), 'new_neighborhood_samples': 1,
                                      'feature_source': str(OLD / 'data/small/processed/paper/node_feat.npy'),
                                      'full_feature_payload_not_persisted': True,
                                      'reconstruct_from': 'frozen_minibatch_arrays.npz input_nodes + original FP32 feature table',
                                      'no_cache_replay_between_runs': True})
    stage('THREE_QUALIFICATION_OBSERVATIONS')
    values = {}
    buffers_seen = set()
    for tag in ['eagerA', 'eagerB', 'compiledC']:
        stage('BEFORE_' + tag)
        before_input = frozen_identity(mb)
        assert before_input == frozen, 'FROZEN_INPUT_CHANGED_BEFORE_RUN'
        assert state_identity(cpu_parameters(models[tag])) == identity, 'INITIAL_PARAMETERS_CHANGED'
        assert opts[tag].state_dict()['state'] == {}, 'INITIAL_OPTIMIZER_STATE_CHANGED'
        ledger = json.loads((R / 'update_ledger.json').read_text()) if (R / 'update_ledger.json').exists() else {'reserved': 0, 'completed': 0, 'entries': []}
        assert ledger['reserved'] < 3
        ledger['reserved'] += 1
        ledger['entries'].append({'tag': tag, 'status': 'RESERVED_BEFORE_CALL'})
        save('update_ledger.json', ledger)
        stage('EXECUTE_' + tag)
        start = time.monotonic()
        if tag == 'compiledC':
            compiled = torch.compile(train_step, dynamic=True)
            loss = compiled(mb, opts[tag], models[tag])
        else:
            loss = train_step(mb, opts[tag], models[tag])
        sync()
        seconds = time.monotonic() - start
        updated, gradients, row = snapshot(tag, models[tag], opts[tag], float(loss))
        after_input = frozen_identity(mb)
        assert after_input == frozen, 'FROZEN_INPUT_CHANGED_AFTER_RUN'
        buffer_ids = {(x['device'], x['storage_ptr']) for x in row['optimizer_buffers']}
        assert buffers_seen.isdisjoint(buffer_ids), 'OPTIMIZER_BUFFER_ALIAS_ACROSS_MODELS'
        buffers_seen.update(buffer_ids)
        row.update(input_before=before_input, input_after=after_input,
                   qualification_call_wall_seconds=seconds,
                   timing_scope='qualification metadata only, not steady-state performance')
        save(tag + '_observation.json', row)
        values[tag] = {'updated': updated, 'gradient': gradients, 'loss': float(loss)}
        ledger['completed'] += 1
        ledger['entries'][-1]['status'] = 'COMPLETED_EXACTLY_ONE_ADAM_STEP'
        save('update_ledger.json', ledger)
    stage('ALL_PARAMETER_COMPARISONS')
    ab = authoritative_update_pair(values, models, 'eagerB')
    ac = authoritative_update_pair(values, models, 'compiledC')
    save('updated_pairs_torch_authority.json', {'A_B': ab, 'A_C': ac})
    comparisons = {'updated_parameter_eagerA_eagerB': ab, 'updated_parameter_eagerA_compiledC': ac}
    for candidate in ['eagerB', 'compiledC']:
        comparisons['gradient_eagerA_' + candidate] = parameter_pairs(values['eagerA']['gradient'], values[candidate]['gradient'], 1e-5, 1e-3)
        comparisons['gradient_eagerA_' + candidate]['scope'] = 'paired fullbatch descriptive comparison; original 16seed FP64 gradient gate not reapplied as a new eligibility gate'
        a = values['eagerA']['loss']
        b = values[candidate]['loss']
        comparisons['loss_eagerA_' + candidate] = {'reference': a, 'candidate': b,
                                                   'abs_difference': abs(a - b),
                                                   'tolerance': 1e-5 + 1e-4 * abs(a),
                                                   'pass': abs(a - b) <= 1e-5 + 1e-4 * abs(a)}
    # Same-gradient first Adam formula is a CPU observation, not an extra optimizer update.
    adam = {}
    for tag in values:
        rows = {}
        for n, before in initial_np.items():
            g = values[tag]['gradient'][n]
            bt = torch.from_numpy(before)
            gt = torch.from_numpy(g)
            expected_tensor = bt - .003 * gt / (gt.abs() + 1e-8)
            expected = expected_tensor.numpy()
            rows[n] = stats(values[tag]['updated'][n], expected, 1e-6, 1e-4)
            rows[n]['original_Torch_CPU_formula_allclose'] = bool(torch.allclose(torch.from_numpy(values[tag]['updated'][n]), expected_tensor, atol=1e-6, rtol=1e-4))
        adam[tag] = rows
    comparisons['first_Adam_same_gradient_CPU_formula'] = adam
    for candidate in ['eagerB', 'compiledC']:
        da = {n: values['eagerA']['updated'][n] - initial_np[n] for n in initial_np}
        db = {n: values[candidate]['updated'][n] - initial_np[n] for n in initial_np}
        delta = parameter_pairs(da, db, 1e-6, 1e-4)
        delta['scope'] = 'signed after-before differences; descriptive only, original gate remains on updated parameters'
        comparisons['update_delta_eagerA_' + candidate] = delta
    attribution = {}
    for label, candidate, pair in [('A_B', 'eagerB', ab), ('A_C', 'compiledC', ac)]:
        attribution[label] = {}
        for name, row in pair['parameters'].items():
            cases = []
            for failure in row['first_failures']:
                point = tuple(failure['coordinate'])
                cases.append({**failure, 'initial': float(initial_np[name][point]),
                              'gradient_reference': float(values['eagerA']['gradient'][name][point]),
                              'gradient_candidate': float(values[candidate]['gradient'][name][point]),
                              'signed_delta_reference': float(values['eagerA']['updated'][name][point] - initial_np[name][point]),
                              'signed_delta_candidate': float(values[candidate]['updated'][name][point] - initial_np[name][point])})
            attribution[label][name] = {'failed_elements': row['failed_elements'], 'examples': cases}
    save('failure_element_attribution.json', attribution)
    save('parameter_comparisons.json', comparisons)
    status = classify(ab, ac)
    if status != 'COMPARATOR_OR_IDENTITY_DEFECT':
        if not comparisons['loss_eagerA_eagerB']['pass']:
            status = 'EAGER_EAGER_NUMERIC_VARIABILITY'
        elif status == 'SAME_BATCH_NUMERIC_CONTROL_PASS' and not comparisons['loss_eagerA_compiledC']['pass']:
            status = 'COMPILED_PATH_NUMERIC_NONALIGNMENT'
    counters = {str(k): {str(n): int(v) for n, v in c.items()} for k, c in torch._dynamo.utils.counters.items()}
    save('compiler_metadata.json', {'entry': 'torch.compile(train_step,dynamic=True)',
                                    'counters': counters, 'cache_namespace': str(R / 'cache'),
                                    'qualification_only_not_performance': True})
    save('numeric_result.json', {'scientific_status': status, 'eager_eager_update_pass': ab['numerical_pass'],
                                'eager_compiled_update_pass': ac['numerical_pass'],
                                'actual_qualification_updates': 3, 'formal_updates': 0,
                                'single_frozen_batch': True, 'initial_state_pass': True,
                                'input_SHA_before_after_allthree_pass': True,
                                'all_losses': {n: x['loss'] for n, x in values.items()},
                                'Torch_peak_allocated_bytes': torch.cuda.max_memory_allocated(),
                                'Torch_peak_reserved_bytes': torch.cuda.max_memory_reserved(),
                                'compiler_bug': 'NOT_ESTABLISHED', 'A61_STOP_unchanged': True,
                                'next_GPU_task': False})
    stage('NUMERIC_OBSERVATIONS_COMPLETE_STOP')


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        save('runner_failure.json', {'error': repr(exc), 'traceback': traceback.format_exc(),
                                    'status': 'NUMERIC_INSTRUMENTATION_INCOMPLETE_OR_SCIENTIFIC_STOP',
                                    'no_automatic_retry': True})
        raise
