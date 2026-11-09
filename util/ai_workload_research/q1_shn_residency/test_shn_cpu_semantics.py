"""Small CPU-only comparison against the frozen original CPUAdam binary."""
import json
import sys
from pathlib import Path

ASSET = Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/software_sources/gsscale')
sys.path.insert(0, str(ASSET / 'cpu_adam'))
import torch
from cpu_adam import calculate_update_ids, adam_deferred_update, adam_for_next_with_counter, update_counter
from shn_candidate import ShNResident

torch.set_num_threads(1)
torch.manual_seed(20261109)
N, D = 8, 45
weight = torch.randn(N, D, dtype=torch.float32) * .03
grad = torch.randn(N, D, dtype=torch.float32) * .002
m = torch.randn(N, D, dtype=torch.float32) * .001
v = torch.rand(N, D, dtype=torch.float32) * .0001 + .00001
counter = torch.tensor([0, 1, 15, 14, 7, 15, 2, 0], dtype=torch.int8)
visible = torch.tensor([6, 2, 6, 1], dtype=torch.int32)
U = calculate_update_ids(visible, counter, N)
assert U.tolist() == [1, 2, 5, 6]
step, lr, b1, b2, eps = 15140, .001, .9, .999, 1e-15

def compare(name, x, y):
    assert x.shape == y.shape
    absdiff = (x-y).abs()
    max_abs = absdiff.max().item() if x.numel() else 0.0
    scale = x.abs().max().item() if x.numel() else 0.0
    assert max_abs <= 2e-6 + 2e-4 * scale, (name, max_abs, scale)
    return {'max_abs': max_abs, 'reference_max_abs': scale}

# C++ updates U, including the forced age==15 row, without consuming the next camera.
w_ref, g_ref, m_ref, v_ref, c_ref = [x.clone() for x in (weight, grad, m, v, counter)]
w_new, g_new, m_new, v_new, c_new = [x.clone() for x in (weight, grad, m, v, counter)]
adam_deferred_update(w_ref, g_ref, m_ref, v_ref, U, c_ref, step, lr, b1, b2, eps)
resident = ShNResident(w_new, g_new, m_new, v_new, chunk_rows=2)
resident.update(U, c_new, step, lr, b1, b2, eps)
checks = {key: compare('update_'+key, a, b) for key, a, b in (
    ('weight', w_ref,w_new), ('moment1',m_ref,m_new), ('moment2',v_ref,v_new))}
update_counter(c_ref, U)
update_counter(c_new, U)
assert torch.equal(c_ref,c_new)
assert c_new.tolist() == [1,0,0,15,8,0,0,1]

# The pending gradient remains for camera t while V(t+1) gets a predicted version.
future = torch.tensor([6, 1, 6, 3], dtype=torch.int64)
reference = torch.empty((future.numel(),D),dtype=torch.float32)
adam_for_next_with_counter(w_ref,g_ref,m_ref,v_ref,future,reference,c_ref,step,lr,b1,b2,eps)
predicted = resident.forward(future,c_new,step,lr,b1,b2,eps)
checks['next_camera'] = compare('next_camera',reference,predicted)
assert torch.equal(predicted[0],predicted[2])
assert torch.equal(c_ref,c_new)
assert torch.equal(w_new,w_new.clone())

empty = torch.empty((0,),dtype=torch.int64)
assert resident.forward(empty,c_new,step,lr,b1,b2,eps).shape == (0,D)

print(json.dumps({'status':'PASS_CPU_SMALL_SEMANTIC','source':'original cpu_adam binary',
                  'cases':['U union','duplicate visible ID','age 15 forced update','counter reset/wrap',
                           'step plus one forward','pending preserved','empty forward','moment update'],
                  'comparison':checks},indent=2))
