
# Execution context

- Repository: `swayhrl/accel-sim-framework`; execution branch `hrl/awma-r101-transient-l2-sim-capture-109-v1` from exact handoff `6533872601bb81dae1475b35d365f9dbe418cb23`.
- Node/GPU: `NVIDIA GeForce RTX 4080, GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59, 580.178.04`; all CUDA execution was serial under `/data/c16/locks/c16_gpu_campaign.lock`.
- Input: accepted R101 payload `1b0496a115ddaa647f8896a20e5711a125e02ab8bb2f7d47dc5f2fbd7693a234`, 44×512×512 BF16, Qwen2.5-0.5B-Instruct revision `7ae557604adf67be50417f59c2c2f167def9a775`. No model download or gradient generation.
- Arithmetic: pinned HiMuon `af89eda9a0176effed99e1fe19cc1f8a1a2c9588`, five steps, `(3.4445,-4.7750,2.0315)`, XXT → BA → BMM-add; accepted output SHA `36aaed3f8360aa099301ae1d705bc2e6ab5ba61586adaf7ead93ecab808dc1b0`.
- Full capture ROI: `R101_L512_FULL5_WITH_NORMALIZATION_V1`; cuProfilerStart just before normalization, cuProfilerStop after fifth BMM-add. Selector is ROI marker plus exact 18-kernel count, **not** the census global launch index. The entire 18-member list was appended by one producer process/context, never concatenated from shards.
- Exact author-listed XXT/BA Triton launch configs were frozen before canaries solely to match accepted R101R1 function/grid/block strata, not selected from performance. The unchanged author kernels and exact output SHA passed the driver audit and payload-free launch census.
- Resource admission: first real complete iteration 404039876 compressed raw bytes; conservative full estimate 2424239256 bytes versus frozen cap 34359738368. Formal guard reason: `None`; peak raw 2039406264 bytes, peak host RSS 714788864 bytes.
