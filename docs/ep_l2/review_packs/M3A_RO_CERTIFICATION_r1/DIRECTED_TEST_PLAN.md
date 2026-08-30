# Future functional directed plan

Test single/multi-sector read miss; merged readers; late merge before first fill and after partial/all-ready; read/write same-line exclusion; atomic and writeback exclusion; stale fill generation; L2->ICNT backpressure; address reuse/new epoch; and terminal drain. Each test must compare baseline and feature-on terminal state, descriptor conservation, ordered responses, and no leaked pending object.
