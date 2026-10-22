# Root handoff commands (NOT executed against production by this candidate)

Use final actual Q and final spec, never the existing NOT_REGISTERED / NOT_LAUNCHABLE drafts. Supply these three exact values to the root shell:

```bash
qualification_path='/actual/root-reviewed/final/E/QUALIFICATION.json'
spec_path='/actual/root-reviewed/final/E/SPEC.json'
tools_publication_commit='ACTUAL_COMMITTED_AND_REMOTE_READ_BACK_E_TOOLS_COMMIT'
e2_candidate='/tmp/e2_detach_final_adoption_candidate'
e2_generated='/tmp/e2_detach_final_adoption_candidate/generated'
e2_pack='/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1'
e2_tools='/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1/util/ep_l2/mechanism_e'
python3 "$e2_candidate/audit_source_switch.py"
python3 "$e2_candidate/prepare_bundle.py" --qualification "$qualification_path" --spec "$spec_path"
```

Root now independently verifies `OLD50_SEAL.json`, resource/input/native qualification and source-switch helper quiescence, and installs the four generated metadata files at `$e2_pack/final_adoption/` plus the 11 runtime files at `$e2_tools/`. Installation and commit/push/remote-readback are root's production actions, not actions the tmp generator performs. Do not include tmp tests as runtime. Do not re-register Q before generating old50 seal and adoption. Do not overwrite final Q/spec bytes after the generation.

After root actually publishes/reads back exact installed source, construct CLIENT and inspect its preservation diff:

```bash
python3 "$e2_candidate/prepare_client.py" --runtime "$e2_generated/runtime" --publication-commit "$tools_publication_commit" --qualification "$qualification_path" --manifest "$e2_pack/final_adoption/FINAL_MANIFEST.json" --out "$e2_candidate/CLIENT_CANDIDATE.json"
```

This checks all local published Git blobs against the complete source pins; root separately verifies the remote commit and atomically installs the candidate as original CLIENT only at quiescence. Old main61/capacity namespace and frozen ledger policies remain unchanged.

Then root may execute the following in one fresh parent. It does not reserve/start an application; it adopts exact one-point scope, registers the real Q and binds one spec using original central API.

```bash
PYTHONPATH="$e2_tools" python3 - "$e2_pack/final_adoption/SPEC.json" <<'PY'
import sys,json
from pathlib import Path
from coordinator import Coordinator,digest
import detach_diagnostic_policy as dp
import detach_validation as dv
s=json.loads(Path(sys.argv[1]).read_text())
a=dp.authority();m=a.authority();a.check_spec(m,s)
qpath=m['scientific_binding']['qualification']['path']
assert digest(qpath)==s['qualification_id']
q=json.loads(Path(qpath).read_text())
dv.configure_binding(q['detach_observer_diagnostic']['validation_scope'])
c=Coordinator()
print(c.adopt_detach_observer_batch())
assert c.register_qualification(qpath)==s['qualification_id']
print(c.bind_detach_observer_condition(s))
PY
```

After verifying actual adoption/Q/binding and final resources, root invokes the **same original controller**, not a worker launch nor another controller:

```bash
python3 "$e2_tools/controller.py" --once --queue "$e2_pack/final_adoption/QUEUE.json"
```

The queue is one exact F endpoint with pairs[]. Controller acquires original unique lock and uses original durable wait collector and resource guards. Removed global time/count/concurrency caps remain null/resource-only. Exact one-reservation cap still applies; no failure retry. Full endpoint validation/pair rejection remains intact. No nohup/background launch is introduced here.
