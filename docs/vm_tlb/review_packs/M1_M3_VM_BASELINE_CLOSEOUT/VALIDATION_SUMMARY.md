# Validation summary

All direct tests compile against `vm_translation.cc` and PASS: M1 core;
G2-1..G2-4; M2-RF retry/persistence; G3-1, G3-2, G3-2B, G3-2C, G3-3,
G3-4A, G3-4B and G3-5A.  `git diff --check` and a release rebuild pass.

Integrated results:

- M1 disabled/ideal one-kernel LUD transparency: exactly 23,977 cycles and
  IPC 0.8205 in both controls.
- Real LUD, 64KB and 2MB: PTE request/response 4/4, zero misassociation and
  final MSHR/PWQ/walkers 0/0/0.
- Real BFS, 64KB: 5,485 cycles, PTE 19/19 (3 L2-only, 16 DRAM), seven walks,
  17 merges, zero misassociation and final MSHR/PWQ/walkers 0/0/0.
- Sensitivities cover 256/768/1536 L2 entries, 8/32/64 MSHRs, 1/4/16 walkers,
  PWC OFF/FINITE-128/IDEAL, fixed/real PTW, 64KB/2MB and 0/0 vs 10/80 lookup
  service.  Exact values and provenance are in the M3 sensitivity TSV.

Only LUD and BFS were available locally; no unsupported third-workload claim
is made.
