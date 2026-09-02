# Validation summary

`g++ -std=c++17 -I<core>/src tests/vm_core_m1_test.cc`: PASS.

The standard Core+Framework build completed successfully. All trace runs used
the Rodinia short-test archive recorded in S1-B0. QV100 LUD-64 disabled/ideal:
19,673 instructions, 20,923 cycles, IPC 0.9403, L2 3,828/512, DRAM 512/0 in
both modes. RTX3070 LUD-64: 19,673 / 23,429 / 0.8397, L2 3,828/512, DRAM
512/0 in both. BFS-4096 QV100 also had exact key-stat equality; final L2 was
31,094 accesses / 5,726 misses and DRAM reads 4,955 in both modes.

Ideal-only counters prove 2,394 LUD and 49,057 BFS requests were translated
without stalls and with `SimVA == SimPA`.
