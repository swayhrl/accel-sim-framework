# Accel-Sim Offline-Sim V1

Start with `offline/doctor.sh`, then `offline/setup.sh`. Set an already-installed CUDA toolkit in `CUDA_INSTALL_PATH`, source `offline/env.sh`, and invoke `offline/build.sh`. The normal paths are SASS trace-driven replay and PTX execution-driven simulation; neither offline script downloads assets.

Framework and `gpu-simulator/gpgpu-sim` are independent Git repositories. This V1 bundle preserves the simulator architecture and does not carry historic Cache/L2/TLB/AI patches.
