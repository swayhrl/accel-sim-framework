# Primary KV/MoE literature: experiment groups

All results are the authors' results. Our experiments in this planning Goal: **0**. The paired JSON contains15 structured experimental groups with model/input identity, device, control, baseline, result, scope and missing disclosure. Source paragraphs are paraphrased; papers were not reproduced.

## Source identity

| Work | Primary source | Version boundary |
|---|---|---|
| STRATA_OSDI26 | [OSDI 2026; official proceedings pp.1-16](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf) | Use OSDI final. arXiv2508.18572v1 is 2025 preprint; its abstract describes a TTFT5x claim while final abstract reports throughput. Do not mix. |
| HYBRIDKV_ACL26 | [ACL2026 long.594; pp13018-13034](https://aclanthology.org/2026.acl-long.594.pdf) | ACL final read via web. Final PDF SSH fetch timeout; SHA pins arXivv1 only. Do not confuse with AdaptFM2026 same-name head-reconstruction paper. |
| MONOMOE_V1 | [arXiv2609.04244v1; submission metadata19Aug2026; no conference acceptance established](https://arxiv.org/pdf/2609.04244v1) | Paper claims FlashInfer integration; linked directory fetch restricted and guessed README404; do not assert installed implementation availability. |
| PATTERNS_ISCA26 | [ISCA2026; DOI10.1109/ISCA66397.2026.00021;author preprintv5 12May2026](https://arxiv.org/pdf/2510.05497v5) | v3 Orders in Chaos is superseded. ArtifactREADME currently names DeepSeekR1AWQ/KimiK2Thinking vs paperV3/KimiK2: identity drift,not silently equivalent. |
| NOTALL_ICLR26 | [ICLR2026; arXiv2505.16056v4 28Feb2026;official repo citesOpenReview2XMAUP74ig](https://arxiv.org/pdf/2505.16056v4) | OpenReview forum browserchallenge;published ICLR header and authorrepo provide venue confirmation. |

## Experimental group index

| Group | Author evidence class | Exact source location |
|---|---|---|
| S_E2E | AUTHOR_REAL_GPU | [sec5.1-5.2; PDFpp9-11, Fig8-10](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf) |
| S_IO_ABLATION | AUTHOR_REAL_GPU_PLUS_SEPARATELY_LABELED_SIMULATION | [sec4.2/5.3; PDFpp6,11-13](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf) |
| S_GH200 | AUTHOR_REAL_GPU_WITH_ORACLE_ESTIMATE | [sec5.3/Fig14-15; PDFp13](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf) |
| H_QUALITY | AUTHOR_REAL_GPU | [sec4.1/Tables1-2; ACLpdfpp6-7; pinnedarxivpp6-7](https://aclanthology.org/2026.acl-long.594.pdf) |
| H_EFFICIENCY | AUTHOR_REAL_GPU | [sec4.2/Table3; pinnedarxivpp6-7; finalwebTable3](https://aclanthology.org/2026.acl-long.594.pdf) |
| H_ABLATION | AUTHOR_REAL_GPU | [sec4.3-4.4/Tables4-5; pinnedarxivpp7-8](https://aclanthology.org/2026.acl-long.594.pdf) |
| M_SYNTHETIC | AUTHOR_REAL_GPU_SYNTHETIC | [sec4.1-4.3/Table2/Fig8; PDFpp10-11](https://arxiv.org/pdf/2609.04244v1) |
| M_E2E | AUTHOR_REAL_GPU_NATURAL_TEXT | [sec4.4/Fig9; PDFpp11-12](https://arxiv.org/pdf/2609.04244v1) |
| M_ACCURACY | AUTHOR_REAL_GPU_TASK_QUALITY | [sec4.5/Table3; PDFp12](https://arxiv.org/pdf/2609.04244v1) |
| P_ROUTING | AUTHOR_REAL_GPU_ROUTING_COLLECTION | [secIII/V-A; PDFpp3-6,9-10](https://arxiv.org/pdf/2510.05497v5) |
| P_SIM_PPA | AUTHOR_EVENT_DRIVEN_SIMULATION_AND_PPA_ESTIMATE | [secIV-V/Fig12/TableI-II; PDFpp7-12](https://arxiv.org/pdf/2510.05497v5) |
| P_REAL_PLACEMENT | AUTHOR_REAL_GPU | [secVI/Fig17; PDFpp12-13](https://arxiv.org/pdf/2510.05497v5) |
| N_REAL_ROUTES | AUTHOR_MODEL_ROUTING_OBSERVATION | [sec3-5/AppendixD1,D3; PDFpp5-10,16-18](https://arxiv.org/pdf/2505.16056v4) |
| N_TOY | AUTHOR_TRAINED_CONTROLLED_MODELS | [sec3.1/3.3/AppendixD2; PDFpp5-8,17](https://arxiv.org/pdf/2505.16056v4) |
| N_CACHE | AUTHOR_TRACE_CACHE_ANALYSIS_PLUS_NAIVE_RUNTIME | [sec5.2/AppendixF; PDFpp10,27-29](https://arxiv.org/pdf/2505.16056v4) |

## Our inference for the planning portfolio

Q2 must distinguish application capacity transitions from storage footprint and cache-hit statistics. Strata directly covers hierarchical placement, transfer layout and scheduling; the remaining question must survive a current software baseline and account for I/O-kernel contention. HybridKV changes the retained attention context, so its quality contract cannot be substituted for exact full-cache semantics.

Q3 must use naturally generated expert routes and compatible strong software. MonoMoE puts fusion and expert-weight streaming inside an existing GPU kernel; Patterns adds placement/prediction; Not All Models distinguishes model locality from a system's realized benefit. Our residual question therefore needs costs left after these applicable controls, including metadata, duplicate capacity and communication.

These collisions do not establish that every remaining cost is absorbed. They exclude generic proposals based solely on hot experts, KV footprint or isolated operator gains. They do not identify an approved new hardware variable.

## Missing authority and resource disclosure

None of these papers creates local model or input authority for a new experiment. The JSON retains unreported revisions, precision, GPU counts or GPU-hours as missing. Mutable artifact names are not assumed equivalent to a paper checkpoint. MonoMoE code availability remains SOURCE_UNVERIFIED in this bounded check.

Five named public PDFs were downloaded: 31464116 bytes total. Each has an exact SHA256 in private_pdf_manifest. The ACL final PDF timed out over SSH; the final paper was browsed, while the locally pinned HybridKV PDF is explicitly arXivv1.

No model/data downloads, installation, GPU/NVML call or node164 access. Python RSS observations reached57,292KiB, single thread; child/aggregate Goal RSS is not claimed continuously measured. Browser-service network bytes are unmeasured. The Goal owner performs aggregate accounting and publication.
