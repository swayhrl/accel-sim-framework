#!/bin/sh
set -eu
# Main-authorized Performance-First V3 exact10 cohorts only. All prior bytes follow unchanged.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:EP_PERF_PFV3_MIDTAG_FWT_S_G32W16_V1|result:EP_PERF_PFV3_MIDTAG_FWT_S_G32W16_V1|experiment:EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1|result:EP_PERF_PFV3_MIDTAG_FWT_S_G64W8_V1|experiment:EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G32W16_V1|result:EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G32W16_V1|experiment:EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1|result:EP_PERF_PFV3_MIDTAG_FWT_WV_ZERO_RO_G64W8_V1|experiment:EP_PERF_PFV3_MIDTAG_GEMM_S_G32W16_V1|result:EP_PERF_PFV3_MIDTAG_GEMM_S_G32W16_V1|experiment:EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1|result:EP_PERF_PFV3_MIDTAG_GEMM_S_G64W8_V1|experiment:EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G32W16_V1|result:EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G32W16_V1|experiment:EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1|result:EP_PERF_PFV3_MIDTAG_GEMM_WV_ZERO_RO_G64W8_V1|experiment:EP_PERF_PFV3_VECTOR4M_WV_ZERO_RO_1700_V1|result:EP_PERF_PFV3_VECTOR4M_WV_ZERO_RO_1700_V1|experiment:EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1|result:EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1)
   export EP_V3_GLOBAL_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/native/native_v3.py "$@"
   ;;
 esac
fi
# User-authorized Stage II-A remaining48 only. All prior entry bytes remain unchanged.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTC2A48-b31a85e4eb8d32ef-CH-F128-V1|result:E2-DTC2A48-b31a85e4eb8d32ef-CH-F128-V1|experiment:E2-DTC2A48-b31a85e4eb8d32ef-CH-F256-V1|result:E2-DTC2A48-b31a85e4eb8d32ef-CH-F256-V1|experiment:E2-DTC2A48-f7f22a2ccc836a8a-CH-F128-V1|result:E2-DTC2A48-f7f22a2ccc836a8a-CH-F128-V1|experiment:E2-DTC2A48-f7f22a2ccc836a8a-CH-F256-V1|result:E2-DTC2A48-f7f22a2ccc836a8a-CH-F256-V1|experiment:E2-DTC2A48-3722a5c85d91a948-CH-F128-V1|result:E2-DTC2A48-3722a5c85d91a948-CH-F128-V1|experiment:E2-DTC2A48-3722a5c85d91a948-CH-F256-V1|result:E2-DTC2A48-3722a5c85d91a948-CH-F256-V1|experiment:E2-DTC2A48-dd9f695c4f53b083-CH-F128-V1|result:E2-DTC2A48-dd9f695c4f53b083-CH-F128-V1|experiment:E2-DTC2A48-dd9f695c4f53b083-CH-F256-V1|result:E2-DTC2A48-dd9f695c4f53b083-CH-F256-V1|experiment:E2-DTC2A48-2b93f70cd0666c51-CH-F128-V1|result:E2-DTC2A48-2b93f70cd0666c51-CH-F128-V1|experiment:E2-DTC2A48-2b93f70cd0666c51-CH-F256-V1|result:E2-DTC2A48-2b93f70cd0666c51-CH-F256-V1|experiment:E2-DTC2A48-65151d2c661f88f3-CH-F128-V1|result:E2-DTC2A48-65151d2c661f88f3-CH-F128-V1|experiment:E2-DTC2A48-65151d2c661f88f3-CH-F256-V1|result:E2-DTC2A48-65151d2c661f88f3-CH-F256-V1|experiment:E2-DTC2A48-1df9d5479504d9c7-CH-F128-V1|result:E2-DTC2A48-1df9d5479504d9c7-CH-F128-V1|experiment:E2-DTC2A48-1df9d5479504d9c7-CH-F256-V1|result:E2-DTC2A48-1df9d5479504d9c7-CH-F256-V1|experiment:E2-DTC2A48-af7320f9d9dc6629-CH-F128-V1|result:E2-DTC2A48-af7320f9d9dc6629-CH-F128-V1|experiment:E2-DTC2A48-af7320f9d9dc6629-CH-F256-V1|result:E2-DTC2A48-af7320f9d9dc6629-CH-F256-V1|experiment:E2-DTC2A48-2c506bf13c81ff5d-CH-F128-V1|result:E2-DTC2A48-2c506bf13c81ff5d-CH-F128-V1|experiment:E2-DTC2A48-2c506bf13c81ff5d-CH-F256-V1|result:E2-DTC2A48-2c506bf13c81ff5d-CH-F256-V1|experiment:E2-DTC2A48-dc7a91531846c113-CH-F128-V1|result:E2-DTC2A48-dc7a91531846c113-CH-F128-V1|experiment:E2-DTC2A48-dc7a91531846c113-CH-F256-V1|result:E2-DTC2A48-dc7a91531846c113-CH-F256-V1|experiment:E2-DTC2A48-db89be14146b9163-CH-F128-V1|result:E2-DTC2A48-db89be14146b9163-CH-F128-V1|experiment:E2-DTC2A48-db89be14146b9163-CH-F256-V1|result:E2-DTC2A48-db89be14146b9163-CH-F256-V1|experiment:E2-DTC2A48-ffc8a89493c8a211-CH-F128-V1|result:E2-DTC2A48-ffc8a89493c8a211-CH-F128-V1|experiment:E2-DTC2A48-ffc8a89493c8a211-CH-F256-V1|result:E2-DTC2A48-ffc8a89493c8a211-CH-F256-V1|experiment:E2-DTC2A48-c885293ad99e21ee-CH-F128-V1|result:E2-DTC2A48-c885293ad99e21ee-CH-F128-V1|experiment:E2-DTC2A48-c885293ad99e21ee-CH-F256-V1|result:E2-DTC2A48-c885293ad99e21ee-CH-F256-V1|experiment:E2-DTC2A48-79f8ab6241faeed6-CH-F128-V1|result:E2-DTC2A48-79f8ab6241faeed6-CH-F128-V1|experiment:E2-DTC2A48-79f8ab6241faeed6-CH-F256-V1|result:E2-DTC2A48-79f8ab6241faeed6-CH-F256-V1|experiment:E2-DTC2A48-977a2f7007cb1f96-CH-F128-V1|result:E2-DTC2A48-977a2f7007cb1f96-CH-F128-V1|experiment:E2-DTC2A48-977a2f7007cb1f96-CH-F256-V1|result:E2-DTC2A48-977a2f7007cb1f96-CH-F256-V1|experiment:E2-DTC2A48-769e6d9fd5f9cd53-CH-F128-V1|result:E2-DTC2A48-769e6d9fd5f9cd53-CH-F128-V1|experiment:E2-DTC2A48-769e6d9fd5f9cd53-CH-F256-V1|result:E2-DTC2A48-769e6d9fd5f9cd53-CH-F256-V1|experiment:E2-DTC2A48-e5638b94095098ac-CH-F128-V1|result:E2-DTC2A48-e5638b94095098ac-CH-F128-V1|experiment:E2-DTC2A48-e5638b94095098ac-CH-F256-V1|result:E2-DTC2A48-e5638b94095098ac-CH-F256-V1|experiment:E2-DTC2A48-16f4c42373e4961e-CH-F128-V1|result:E2-DTC2A48-16f4c42373e4961e-CH-F128-V1|experiment:E2-DTC2A48-16f4c42373e4961e-CH-F256-V1|result:E2-DTC2A48-16f4c42373e4961e-CH-F256-V1|experiment:E2-DTC2A48-731af5428c4b8155-CH-F128-V1|result:E2-DTC2A48-731af5428c4b8155-CH-F128-V1|experiment:E2-DTC2A48-731af5428c4b8155-CH-F256-V1|result:E2-DTC2A48-731af5428c4b8155-CH-F256-V1|experiment:E2-DTC2A48-b33381cf25d44359-CH-F128-V1|result:E2-DTC2A48-b33381cf25d44359-CH-F128-V1|experiment:E2-DTC2A48-b33381cf25d44359-CH-F256-V1|result:E2-DTC2A48-b33381cf25d44359-CH-F256-V1|experiment:E2-DTC2A48-977e34578994c3d2-CH-F128-V1|result:E2-DTC2A48-977e34578994c3d2-CH-F128-V1|experiment:E2-DTC2A48-977e34578994c3d2-CH-F256-V1|result:E2-DTC2A48-977e34578994c3d2-CH-F256-V1|experiment:E2-DTC2A48-b41cc74c66ca6ed4-CH-F128-V1|result:E2-DTC2A48-b41cc74c66ca6ed4-CH-F128-V1|experiment:E2-DTC2A48-b41cc74c66ca6ed4-CH-F256-V1|result:E2-DTC2A48-b41cc74c66ca6ed4-CH-F256-V1|experiment:E2-DTC2A48-3f85d1878aba9f04-CH-F128-V1|result:E2-DTC2A48-3f85d1878aba9f04-CH-F128-V1|experiment:E2-DTC2A48-3f85d1878aba9f04-CH-F256-V1|result:E2-DTC2A48-3f85d1878aba9f04-CH-F256-V1|experiment:E2-DTC2A48-0e62c67daa020853-CH-F128-V1|result:E2-DTC2A48-0e62c67daa020853-CH-F128-V1|experiment:E2-DTC2A48-0e62c67daa020853-CH-F256-V1|result:E2-DTC2A48-0e62c67daa020853-CH-F256-V1)
   export DTC_STAGEII_REMAINING48_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/dtc_stage_iia_remaining48_20261104_v1/tools/stage2_frontend.py "$@"
   ;;
 esac
fi
# User-authorized Stage II-A exact first16 only. Every previous route byte follows unchanged.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTC2A16-4114a3dc0d06b55b-CH-F128-V1|result:E2-DTC2A16-4114a3dc0d06b55b-CH-F128-V1|experiment:E2-DTC2A16-4114a3dc0d06b55b-CH-F256-V1|result:E2-DTC2A16-4114a3dc0d06b55b-CH-F256-V1|experiment:E2-DTC2A16-6df3a84b612086e8-CH-F128-V1|result:E2-DTC2A16-6df3a84b612086e8-CH-F128-V1|experiment:E2-DTC2A16-6df3a84b612086e8-CH-F256-V1|result:E2-DTC2A16-6df3a84b612086e8-CH-F256-V1|experiment:E2-DTC2A16-d984ea5475a581ad-CH-F128-V1|result:E2-DTC2A16-d984ea5475a581ad-CH-F128-V1|experiment:E2-DTC2A16-d984ea5475a581ad-CH-F256-V1|result:E2-DTC2A16-d984ea5475a581ad-CH-F256-V1|experiment:E2-DTC2A16-eededb785179fc04-CH-F128-V1|result:E2-DTC2A16-eededb785179fc04-CH-F128-V1|experiment:E2-DTC2A16-eededb785179fc04-CH-F256-V1|result:E2-DTC2A16-eededb785179fc04-CH-F256-V1|experiment:E2-DTC2A16-f437190767aaed49-CH-F128-V1|result:E2-DTC2A16-f437190767aaed49-CH-F128-V1|experiment:E2-DTC2A16-f437190767aaed49-CH-F256-V1|result:E2-DTC2A16-f437190767aaed49-CH-F256-V1|experiment:E2-DTC2A16-ae34174fbbdf83b2-CH-F128-V1|result:E2-DTC2A16-ae34174fbbdf83b2-CH-F128-V1|experiment:E2-DTC2A16-ae34174fbbdf83b2-CH-F256-V1|result:E2-DTC2A16-ae34174fbbdf83b2-CH-F256-V1|experiment:E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1|result:E2-DTC2A16-e7bb67e63e3c3847-CH-F128-V1|experiment:E2-DTC2A16-e7bb67e63e3c3847-CH-F256-V1|result:E2-DTC2A16-e7bb67e63e3c3847-CH-F256-V1|experiment:E2-DTC2A16-fc0705ae3721e999-CH-F128-V1|result:E2-DTC2A16-fc0705ae3721e999-CH-F128-V1|experiment:E2-DTC2A16-fc0705ae3721e999-CH-F256-V1|result:E2-DTC2A16-fc0705ae3721e999-CH-F256-V1)
   export DTC_STAGEII_FIRST16_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/dtc_stage_iia_first16_20261104_v1/tools/stage2_frontend.py "$@"
   ;;
 esac
fi
# Explicit padding-only opt-in. Every original route byte follows unchanged.
dtc_padding_route_hold() {
 printf '{"status":"HOLD","reason":"%s","scientific_starts":0}\n' "$1" >&2
 exit 2
}
dtc_padding_route_count=0
dtc_padding_route_bad=0
for dtc_padding_route_arg in "$@"; do
 case "$dtc_padding_route_arg" in
  --padding-only-admission-v1) dtc_padding_route_count=$((dtc_padding_route_count + 1));;
  --padding-only-admission*) dtc_padding_route_bad=1;;
 esac
done
if [ "$dtc_padding_route_bad" -ne 0 ]; then
 dtc_padding_route_hold UNKNOWN_PADDING_FLAG
fi
if [ "$dtc_padding_route_count" -ne 0 ]; then
 [ "$dtc_padding_route_count" -eq 1 ] || dtc_padding_route_hold DUPLICATE_PADDING_FLAG
 [ "$#" -ge 3 ] || dtc_padding_route_hold INCOMPLETE_PADDING_COMMAND
 case "$1:$2:$3" in
  experiment:prepare:E2-DTCL2MLP-*|experiment:inspect:E2-DTCL2MLP-*|experiment:run-native:E2-DTCL2MLP-*) ;;
  *) dtc_padding_route_hold PADDING_SCOPE_OR_OPERATION_MISMATCH;;
 esac
 dtc_padding_route_validate_tail() {
  shift 3
  dtc_padding_route_projects=0
  dtc_padding_route_tailflags=0
  while [ "$#" -gt 0 ]; do
   case "$1" in
    --project)
     [ "$#" -ge 2 ] || dtc_padding_route_hold MISSING_PROJECT_VALUE
     [ "$2" = DTC_L1 ] || dtc_padding_route_hold WRONG_PADDING_PROJECT
     dtc_padding_route_projects=$((dtc_padding_route_projects + 1))
     shift 2;;
    --padding-only-admission-v1)
     dtc_padding_route_tailflags=$((dtc_padding_route_tailflags + 1))
     shift;;
    *) dtc_padding_route_hold UNKNOWN_PADDING_ARGUMENT;;
   esac
  done
  [ "$dtc_padding_route_projects" -eq 1 ] || dtc_padding_route_hold PROJECT_NOT_EXACTLY_ONCE
  [ "$dtc_padding_route_tailflags" -eq 1 ] || dtc_padding_route_hold PADDING_FLAG_NOT_IN_OPTION_TAIL
 }
 dtc_padding_route_validate_tail "$@"
 exec /usr/bin/python3 -B '/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/future_memory_admission_v1/memory_frontend.py' "$@"
fi
#!/bin/sh
set -eu
# New EP performance Goal only; registered exact cohort and immutable runtime checks are in the frontend.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:EP_PERF_*)
   export EP_FULL_PERF_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/ep_l2_full_workload_performance_20261027_v1/tools/ep_perf_frontend.py "$@"
   ;;
 esac
fi
#!/bin/sh
set -eu
# Exact authorized DTC L2-MLP route; all previous routes retained byte-for-byte.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTCL2MLP-*|result:E2-DTCL2MLP-*)
   exec /usr/bin/python3 -B /root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/future_memory_admission_v1/memory_frontend.py "$@"
   ;;
 esac
fi
# New exact multiworkload cohorts only. Complete reviewed prior entry bytes follow unchanged.
if [ "$#" -ge 3 ]; then
 case "$3" in
  EP_MULTI_VECTOR_F_ET0_20261027_V1|EP_MULTI_VECTOR_F_ET1_20261027_V1|EP_MULTI_CONV_S_ET1_20261027_V1|EP_MULTI_FWT_S_ET1_20261027_V1|EP_MULTI_CFD_S_ET1_20261027_V1|EP_MULTI_DWT_S_ET1_20261027_V1|EP_MULTI_GAUSSIAN_S_ET1_20261027_V1|EP_MULTI_SAD_S_ET1_20261027_V1|EP_MULTI_SGEMM_S_ET1_20261027_V1|EP_MULTI_ATAX_S_ET1_20261027_V1|EP_MULTI_BICG_S_ET1_20261027_V1|EP_MULTI_GESUMMV_S_ET1_20261027_V1)
   export EP_MULTIWORKLOAD_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/ep_l2_multiworkload_event_timeline_20261027_v1/tools/native_multi_dispatch.py "$@"
   ;;
 esac
fi
#!/bin/sh
set -eu
# Exact finite DTC HASH18 route; all preexisting native routes retained byte-for-byte.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTCHASH18-*|result:E2-DTCHASH18-*)
   exec /usr/bin/python3 -B /root/data/dtc_hash_downstream18_20261027_v1/tools/ds18_frontend.py "$@"
   ;;
 esac
fi
# Exact post-run parsing acceptance only. Complete prior entry follows unchanged.
if [ "$#" -ge 3 ]; then
 case "$1:$2" in
  experiment:accept-final-scopes|result:accept-final-scopes)
   case "$3" in
    EP_MATCH_D_S_L0_20261027_V1|EP_MATCH_D_S_L1_20261027_V1|EP_MATCH_D_FMT_L0_20261027_V1|EP_MATCH_D_FMT_L1_20261027_V1|EP_MATCH_D_F_L1_20261027_V1)
     export EP_MATCHED_SCOPE_ACCEPT_ENTRY=1
     export EP_MATCHED_NATIVE_ENTRY=1
     exec /usr/bin/python3 -B /root/data/ep_l2_matched_baseline_t_dram_latency_20261027_v1/tools/accept_final_scopes.py "$@"
     ;;
   esac
   ;;
 esac
fi
#!/bin/sh
set -eu
# Exact matched finite routes; original bytes remain below unchanged.
if [ "$#" -ge 3 ]; then
 case "$3" in
  EP_MATCH_D_S_L0_20261027_V1|EP_MATCH_D_S_L1_20261027_V1|EP_MATCH_D_FMT_L0_20261027_V1|EP_MATCH_D_FMT_L1_20261027_V1|EP_MATCH_D_F_L1_20261027_V1|EP_MATCH_D_F_L0_REF_20261027_V1)
   export EP_MATCHED_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/ep_l2_matched_baseline_t_dram_latency_20261027_v1/tools/native_matched_dispatch.py "$@"
   ;;
 esac
fi
#!/bin/sh
set -eu
# New exact capacity cohorts only. All prior bytes below are preserved.
if [ "$#" -ge 3 ]; then
 case "$3" in
  EP_TAGFLOW_VECTOR_A_S64_W16_T1_20261027_V1|EP_TAGFLOW_VECTOR_B_S64_W8_T1_20261027_V1|EP_TAGFLOW_VECTOR_C_S32_W16_T1_20261027_V1|EP_TAGFLOW_VECTOR_D_S32_W8_T1_20261027_V1|EP_TAGFLOW_VECTOR_TOFF_1_20261027_V1|EP_TAGFLOW_VECTOR_TOFF_2_20261027_V1)
   export EP_TAG_CAPACITY_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/ep_tag_capacity_scaling_20261027_v1/tools/native_capacity_dispatch.py "$@"
   ;;
 esac
fi
#!/bin/sh
set -eu
if [ "$#" -ge 3 ] && [ "$3" = "EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2" ]; then
 exec /usr/bin/python3 -B /root/data/ep_tag_reservation_lifetime_20261026_v1/tools_v3/native_dispatch.py "$@"
fi
#!/bin/sh
set -eu
# Explicit finite RECOVER12 route; all prior DTC and EP routes remain byte-identical.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-AEREPAIR-RECOVER12-*|result:E2-AEREPAIR-RECOVER12-*)
   exec /usr/bin/python3 -B /root/data/dtc_failure_repair_20261025_v1/validation_storage_recovery12_v1/tools/recovery12_frontend_v1.py "$@"
   ;;
 esac
fi
#!/bin/sh
set -eu
if [ "$#" -ge 3 ] && { [ "$3" = "EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V1" ] || [ "$3" = "EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V1" ]; }; then
 case "$2" in register|run|run-native)
  printf '%s
' '{"status":"V1_SUPERSEDED_ZERO_SCIENTIFIC_BUDGET","automatic_retry":false}' >&2
  exit 2;;
 esac
fi
if [ "$#" -ge 3 ] && { [ "$3" = "EP_NATIVE_VECTOR_TAG_LIFETIME_OFF_20261026_V2" ] || [ "$3" = "EP_NATIVE_VECTOR_TAG_LIFETIME_ON_20261026_V2" ]; }; then
 exec /usr/bin/python3 -B /root/data/ep_tag_reservation_lifetime_20261026_v1/tools_v2/native_dispatch.py "$@"
fi
exec /bin/sh /root/data/ep_tag_reservation_lifetime_20261026_v1/tools_v2/prior_native_entry.sh "$@"
