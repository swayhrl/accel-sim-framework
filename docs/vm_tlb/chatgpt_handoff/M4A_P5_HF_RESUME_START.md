# Track B start override — resume P5 after Hugging Face credential provisioning

This file is the current Track-B authorization and overrides the prior admission block once the user has securely provisioned a valid Hugging Face credential on the rented host.

Read:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_P5_HF_RESUME_AND_GOAL_CONTINUE.md`

Current facts:

- rented-host pilot P1–P4 are accepted PASS;
- pilot is `PILOT_BLOCKED` only because no usable Hugging Face credential was available at P5;
- the user may provision the credential interactively on the rented host without exposing it to Codex/chat/Git;
- a valid cached Hugging Face login is sufficient; an exported `HF_TOKEN` variable is not mandatory if `huggingface_hub` can securely resolve the cached credential;
- after exact-model access proof, resume pilot P5–P8;
- if pilot becomes `PILOT_PASS_READY_FOR_GOAL_CAPTURE`, continue immediately in Codex **Goal / 目标 mode** through the full formal M4A-C capture goal without another human pause.

Do not print, commit, archive, or copy back the credential. Do not substitute another model if gated access fails.