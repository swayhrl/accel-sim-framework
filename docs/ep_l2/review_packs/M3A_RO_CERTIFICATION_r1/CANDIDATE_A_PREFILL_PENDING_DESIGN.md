# Candidate A — pre-fill replacement

Transition would be after the last required lower issue. A pending object would need line key/epoch, issued/pending/ready masks, fill ownership/generation, atomic/write-order state, descriptor references and per-request masks, and late-merge routing. Late requests must find the pending object by line+epoch, preserve RAW/WAR exclusion, and roll back to a full entry if capacity/identity checks fail. Since source does not prove a safe request class or a complete moved-state contract, Candidate A is **not ready**.
