# Round16 coordination notes

## Why the two lanes are parallel

The lanes deliberately fail for different reasons:

- Lane F can fail on **semantic/runtime qualification** even before performance: the VJP must be real and pass through the network.
- Lane G can fail on **scientific input authority** before CUDA: real adjacent weight versions are mandatory.

Therefore both should begin now with CPU/source work; neither should be kept idle waiting for the other.

## GPU scheduling

If both lanes become GPU-ready:
1. whichever lane reaches a frozen GPU command first may acquire the shared lock;
2. the other continues CPU/report work or stays quiescent;
3. no priority is inferred from lane letter;
4. do not change a scientific plan merely to fit the other lane's runtime.

## No speculative 174 work

Do not prepare new Accel-Sim traces/configs "in case" either lane becomes positive.
A positive Native boundary still requires ChatGPT review before simulator/mechanism design.

## Deferred side lane

CCE/Liger exact-loss quick falsification remains a documented fallback only.
It may be reconsidered if:
- F and G are both scientifically blocked for reasons that cannot be repaired inside their contracts; and
- a compatible real hidden/label workload and strong exact/no-filter implementation are already locally available.

Do not start it merely because the GPU is idle.
