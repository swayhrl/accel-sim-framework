# Cap10 resource-only Host migration

Pure binder reads the current official registry and all current exact Specs. Every consumed case is skipped regardless of state. It does not install, register, invoke Native, change a controller, or start a model.

`python3 -B bind_unconsumed_resources.py --bindings bindings.json --out <this_private_tree>/bound`

Bindings keys: `scope={global_EP_model_limit:10,scientific_budget_changed:false}`, `module_refs={system:ref,highclock:ref,shared:ref(optional)}`, `policy_ref`, `additional_pinned_refs`. Main must independently review the actual C resource qualification.

The output `SPEC_INDEX.json` records registry SHA, exact original/candidate Spec refs, the protected consumed population, and original budget/remaining/consumed/runtime/native snapshots. No top-level Spec keys can be added or removed. Only resource_module_ref, resource_policy_ref, and pinned_files may change. Source/ELF/input/282/geometry/observer/argv/RO/stages/limits/Native/HostQ/runtime remain equal.

Immediately before installation under Main admission+registry locks: `python3 -B bind_unconsumed_resources.py --verify-index <index>`. Any registry advance or newly consumed case fails closed; rerun the pure binder rather than changing a consumed case. Main alone versions the old unconsumed Specs and prelaunch receipts, changes their admitted SHA, and uses the same originally approved budget. Runtime versions and scoped/global Native need no amendment.

The previous engine native preparation, parser, stage gates, mixed original/new Host peer semantics, and qualification modules are reused unchanged. Running/accepted Specs and their receipts stay untouched. After old active models close naturally, Main alone hands ownership to the cap10 controller.
