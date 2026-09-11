# FAST64 2DConvolution tag-identity Core authority map

Status: **ACTIVE — NARROW EXCEPTION TO THE DEFAULT FORMAL CORE**

## Authority

`95ccdb7a056f2d53f740d90869785cac6d4ee0f5` with runtime
`462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9` remains
the default FAST64 formal Core/runtime identity.  It remains the required
identity for every new non-2DConvolution formal row.

`6587238c60214d99491f4048e28ce8a3458c1509` is a descendant of Core95 on
`hrl/decoupled-l1-m5-2d-reserved-tag-repair-v0`, with Release runtime
`29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1`.
It is the sole authorized final identity for the 2DConvolution Base/IO/OO
triplet and any 2DConvolution cap-resolution control or reacquisition.

The sole functional delta is the `gpu-cache.cc` MSHR-merge tag re-probe
described and unit-regressed in
`FAST64_3_2D_MSHR_TAG_IDENTITY_REPAIR.md`: a merge is allowed only when the
current tag is `HIT` or `HIT_RESERVED`, preventing a second ownerless
`RESERVED` tag against an existing MSHR.  It changes neither DTC policy nor
lower-credit, completion, payload, config, or observer semantics.

## Scope and anti-mixing rule

| Row scope | Required Core/runtime | Status |
|---|---|---|
| New non-2DConvolution FAST64 formal acquisition | Core95 / runtime462 | Default formal identity |
| 2DConvolution Base, IO, OO and cap controls/reacquisition | Core658 / runtime29a | Narrow repair exception |
| Historical bbcbb/Core41 rows | Literal historical identity | Never relabel or promote by this map |

Core658 is not a global supersession or a general Core95-equivalence claim.
One accepted 2DConvolution triplet must use Core658/runtime29a throughout;
the collector must reject an undeclared Core95/Core658 mix.

## FAST64.4 cap-resolution consequence

The Core658 2DConvolution IO@8192 row is retained as
`CAP_BOUND_DIAGNOSTIC_NOT_PRIMARY_RESULT`.  The Core658 IO@1048576 row is a
non-primary high-cap control.  A final common cap may admit an 8192 historical
primary row only after explicit non-binding proof under the cap-resolution
authority; otherwise that row is reacquired under its required literal Core
identity.  No cap identity is silently mixed into the primary matrix.
