# First4PHYS768 spec/config builder (CPU-qualified draft)

180CPU checks passed for exactly2DCONV/GEMM/MVT/BICG, onePHYS768_TAG64x8 point each. Sandbox contains4canonical specs plus byte-identical aliases,4copied input bindings,4exact Aconfigs, MATRIX4 and reference table. Each spec preserves full270 effective options with onlyphysical640->768, original expected kernel/instruction/CTA, binary/libs/runtime_files/environment and dynamic host_cpu=null. Resources are exact copies of A723a fields, not substituted hardcoded defaults.

Root may invoke the builder after its actual execution gates, without running any simulation in this builder:

```sh
python3 -B /root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/B_first4_spec_builder_v1/build_first4_specs.py --output-root /root/data/dtc_perf_first_parallel_exploration_20261104_v1 --logical-root /root/data/dtc_perf_first_parallel_exploration_20261104_v1
```

The builder verifies43 explicit immutable sourceSHA dependencies (Rootauthority0b9cd6,USER9a55,Astructure4001,Aresource723a,4baseline specs/refs/input bindings/configs/runtime assets). It writes only requested output-root configuration/spec/reference files and symlinks to existing verified runtime assets; existingdifferent files cause HOLD with no overwrite. Parent symlink escapes are rejected before directory creation. The dependencies are checked before materialization, not inferred from filenames. No P0rerun, registration, dispatch, grant/lease/authority mutation, actualnativeprepare/terminal call or newservice occurs.

Sandbox logical paths intentionally name finalR3 so canonical spec and MATRIX bytes match Root's later materialization. SPEC_BUILD_REFERENCE_TABLE output_root is observational and changes to Root's actual output location. Do not copy the entire sandbox: invoke the builder. Runtime library symlinks are metadata-only review references, excluded from publishedmembers; binaries/libraries are not duplicated into Git. CPUnegative fixtures are excluded.

CPUqualification executes the exact current native.canonical function extracted byAST with in-memory fake registered/read context only. It creates no fake native registry/grant or dispatch record. Strictterminal and actualprepare are not invoked. API_COMPATIBILITY_REFS records the as-ofsourceSHAs; Root's later forwardstrict adapter changes/actualsourcepins and Cactual qualification remain independent. This package does not override newforward28gate, Tag16HOLD, prepcommit/PROJECT_AUTH or owner.

All4spec SHA and option/config/source diffs are in sandbox/control/SPEC_BUILD_REFERENCE_TABLE.json. Sandbox passed with0R3 writes and0models. Publish only MANIFEST members, not negativefixtures or runtime symlinks.
