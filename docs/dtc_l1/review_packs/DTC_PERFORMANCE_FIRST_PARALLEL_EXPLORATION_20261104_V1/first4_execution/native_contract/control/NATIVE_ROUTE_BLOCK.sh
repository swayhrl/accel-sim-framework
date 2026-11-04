# User-authorized Performance-First PHYS768 first4 only; all prior entry bytes preserved.
if [ "$#" -ge 3 ]; then
 case "$1:$3" in
  experiment:E2-DTCPF4-d984ea5475a581ad-DH-PHYS768-V1|result:E2-DTCPF4-d984ea5475a581ad-DH-PHYS768-V1|experiment:E2-DTCPF4-fc0705ae3721e999-DH-PHYS768-V1|result:E2-DTCPF4-fc0705ae3721e999-DH-PHYS768-V1|experiment:E2-DTCPF4-f437190767aaed49-DH-PHYS768-V1|result:E2-DTCPF4-f437190767aaed49-DH-PHYS768-V1|experiment:E2-DTCPF4-ae34174fbbdf83b2-DH-PHYS768-V1|result:E2-DTCPF4-ae34174fbbdf83b2-DH-PHYS768-V1)
   export DTC_PERFFIRST_FIRST4_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B /root/data/dtc_perf_first_parallel_exploration_20261104_v1/tools/perf4_frontend.py "$@"
   ;;
 esac
fi
