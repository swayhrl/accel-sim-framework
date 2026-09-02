# Changed-file scope

Core changes are limited to the DTC IO helper/model, shader IO request/response
and statistics plumbing, deadlock diagnostics, and deterministic common-model
tests. Conventional L1D remains instantiated for non-IO/mode-later traffic but
is not the cacheable IO-read backend.

Framework changes are limited to M2 evidence, counter documentation, strict
summary parsing, and this review pack. No ChatGPT-owned handoff file changed.
