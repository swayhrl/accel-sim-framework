# R22F1 scientific STOP

`R22F1_FAMILY_GAP_UNRESOLVED`.

The real sorted-graph OAM-S frame55 energy→forces execution yielded exactly two TP callsites, layer0 and layer1, each with one forward and one force backward. Each exact input, TPProblem/JIT identity and real backward upstream gradient is hash-closed. Atomic Aorder and deterministic Dready on those same tensors passed forward and required-gradient `5e-5` comparisons.

Without any new profiler, bundled CUDA-event replay gave aggregate forward Aorder−Dready -0.272 µs, backward +0.334 µs, combined +0.062 µs (+0.029%). Combined group gaps changed sign; the 3×MAD gate failed. This cannot affirm either a positive or negative same-input TP-family cost. Exact direct fixup timing was unavailable, so its low-overhead isolated cost remains unknown.

R22F's NSYS diagnostic (+26.752 µs deterministic net TP cost) and full-model uninstrumented ready-graph benefit (13.955 µs / 2.878%) remain observations at different boundaries. R22F1 does not turn either into a causal explanation. Do not run Donline or pursue an R21A target-family mechanism on this evidence.
