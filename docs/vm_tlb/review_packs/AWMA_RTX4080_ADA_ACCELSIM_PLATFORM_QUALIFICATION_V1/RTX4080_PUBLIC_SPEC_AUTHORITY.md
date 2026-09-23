# RTX4080 public specification authority

Primary public authorities:

1. NVIDIA GeForce RTX4080 family specifications: https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4080-family/
   - 9728 CUDA cores, 2.51 GHz boost, 2.21 GHz base, 16 GB GDDR6X, 256-bit interface, CUDA capability 8.9.
2. NVIDIA CUDA GPU compute-capability table: https://developer.nvidia.com/cuda/gpus
   - GeForce RTX4080 is compute capability 8.9.
3. NVIDIA Ada GPU Architecture whitepaper: https://images.nvidia.com/aem-dam/Solutions/geforce/ada/nvidia-ada-gpu-architecture.pdf
   - Appendix B identifies RTX4080 AD103 with 76 SMs, 128 CUDA cores/SM, 2505 MHz boost, 22.4 Gbps GDDR6X, 716.8 GB/s, 65536 KB L2, 9728 KB aggregate L1/shared, 19456 KB register file, and eight 32-bit memory controllers.

These sources establish scale and bandwidth class. They do not establish proprietary scheduler, cache-replacement, exact issue-port, or TLB/PTW details.
