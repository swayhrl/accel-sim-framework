# Candidate B — all-ready response tail

Transition would occur only after all required sectors are ready, moving line key/epoch plus ordered descriptor/requester references, response-queued state, atomic/order state, and response-tail cursor into a tail object. New same-line requests require a defined tag-state/epoch lookup; response queue backpressure must retain order and release only after final descriptor commit. Partial fills cannot enter B. This is simpler than A but its all-ready-to-final-retirement interval is not emitted, so it is **not ready**.
