#!/usr/bin/env python3
print('PROBE_START', flush=True)
import torch
print('PROBE_TORCH_IMPORTED', flush=True)
x = torch.ones(64, device='cuda:0')
print('PROBE_CUDA_ALLOCATED', flush=True)
y = x + 1
torch.cuda.synchronize()
print('PROBE_CUDA_KERNEL_COMPLETE', float(y[0].item()), flush=True)
