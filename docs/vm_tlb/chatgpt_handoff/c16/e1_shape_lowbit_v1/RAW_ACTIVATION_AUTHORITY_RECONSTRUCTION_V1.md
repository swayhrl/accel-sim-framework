# E1 RAW Activation Authority Reconstruction Note V1

The E1 STOP on node109 is a **recoverable authority-packaging gap**, not evidence that the RAW scientific state is irretrievably missing.

The accepted prior AWMA E1 V2 contract explicitly generated the RAW shape-specific activation authority from an accepted exact RAW replay source by:

1. loading the accepted RAW Qwen2.5-7B deployment;
2. running the accepted S2_TEXT 2048-token sequence;
3. capturing the live Layer0 module input with exact hooks;
4. deriving M256 from the first 256 rows and M1 from the first row;
5. creating a shape-specific direct output oracle for each shape.

Accepted source identity:

- model:
  `Qwen/Qwen2.5-7B-Instruct`
- revision:
  `a09a35458c702b33eeacc393d103063234e8bc28`
- node109 model root used by accepted V8:
  `/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28`
- token source:
  `/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json`
- token SHA256:
  `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`

Relevant accepted implementation source:

`hrl/c16-qwen25-7b-raw-paired-replay-109-v8@e1d210d662ece6975648d04f628eb3f9e938117f`

with:
- `util/vm_tlb/c16/formal_campaign/v8_raw_full_stream.py`
- `util/vm_tlb/c16/formal_campaign/v8_selective_loader.py`

Accepted AWMA contract that explicitly authorized this reconstruction method:

`hrl/awma-109-e1-shape-oracle-moe-harness-handoff-v2@38e239642ed506966c9626630cc0c5d47dab8387`

section **E1-S3 — Close raw q_proj/down_proj authority**.

Historical RAW shape-point output SHAs from accepted AWMA E1 V2:

- q_proj M256:
  `6c662b748af24fd67f1871b1a71c7ef134e5b7dd3e7b6d043b0ee32780873c21`
- q_proj M1:
  `b573d074433dd5fb43314fc82a43697ea93c6c7f0016df7faaa32522bf11ddb4`
- down_proj M256:
  `962e2846f8e999bebc3d979d1e73c71e947ddc27c1e9e280d32039a1436c3007`
- down_proj M1:
  `0af0c81eee41d0f1d5aceb7f7d28452c548956a3f4fb4d352ae772f0e6cf4671`

## Authorization

Node109 is authorized to reconstruct the missing RAW q_proj M1/M256 and down_proj M256 activation authorities **only by the accepted exact replay recipe above**.

This is not a new scientific input and does not change the fixed-input contract if all gates below close.

Required gates:

1. exact model revision/root and token SHA match;
2. live Layer0 q_proj/down_proj input hook is used;
3. M256 = exact first 256 rows of the natural M2048 module input;
4. M1 = exact first row of the same natural M2048 module input;
5. reconstructed shape/stride/dtype match the historical AWMA E1 V2 records;
6. direct RAW outputs reproduce the historical output SHAs above;
7. existing retained `/data/c16/v9_raw_module_state.pt` down_proj M1 state is used as an additional cross-check when compatible with its stored schema.

If these gates PASS, freeze the reconstructed activation tensors with explicit SHA receipts and continue the existing E1 Goal from the RAW_FP16 bridge.

If any gate fails, STOP as a genuine scientific authority mismatch. Do not substitute AWQ pools or random/synthetic activations.
