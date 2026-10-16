# Validation scope

`VALIDATION.json` passes28 closeout consistency checks. CPU_TEST_RECEIPTS.json passes all original-file/hash/count/parser comparisons, four negative fixtures, typed dependency probes and20 literal dispatcher-block tests. The result is **feasibility evidence with semantic gaps, not simulator admission**.

The real unmodified frozen parser is compiled with g++ and CUDA type headers only; the linked-library log has no libcuda/libcudart. It parses11,708 records from all four original compressed files. Independent Python decompression checks active lane addresses for stride and delta encodings, exact masks/registers/opcodes/widths/immediate bit patterns and count/terminal scope. Zero-mask records are retained. Header89 and all producer/consumer SHA values remain unchanged. No record is deleted to make a test pass.

The wide-register fixture uses the original measured SM89 executable (SHA b8064d9060ed161e9017dfcd6a3f58bcc7e028a295b4d832b582d70cbe56fb2d), offline cubin extraction and installed nvdisasm12.8 liveness, not a new compilation/native run.64 dynamic witnesses are16 per member,32 R17 and32 R3 consumers. Frozen conversion body is extracted literally for the CPU register tests. The probes establish which metadata is missing; they do not synthesize an ISA, estimate performance or validate downstream Core execution.

Original/patched dispatcher tests use map sentinels solely to exercise literal architecture-selection/error control flow. They do not execute the full constructor, full classifier, simulator or Core. Original89 exit0 is explicitly labeled rejection; candidate89 exit1 remains rejection. A full Framework build and admission canary are intentionally not performed. Candidate is checked but not applied.

Python compile, shell syntax and git diff checks pass. Changed paths are limited to the dedicated review pack and CPU helper directory. The main C16 HEAD and completed native-producer HEAD remain unchanged, no global LATEST_REPORT or main dispatcher modified, GPU lock never requested. No new/changed scientific support domain was adopted.
