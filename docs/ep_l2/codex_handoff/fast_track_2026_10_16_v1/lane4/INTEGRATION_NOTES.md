# Lane 4 current integration notes — review_r3

Authority: `a41bfb55934303a4d4a342762f74a16d137d0316` supersedes prior
application qualification and execution-state wording. Original mechanism,
resource and oracle contract `6c136e2a...` is unchanged.

Old R0 Core126394be/binary0b504f55, official R1 Corebe651ccf/binary2d2fb082,
and Lane4's runtime-equivalent candidate b8b3d55b/binary63f26de2 cannot qualify
as repaired application evidence. Frozen bytes, fixture passes and original
execution terminals remain. The OLD_STATIC 1.721259x reference is historical
only; it is neither newly invalidated by the FT finding nor a repaired ceiling.

Lane1 owns official R0.1 and separate R1.1 releases. Lane5 independently checks
physical_bank_clock and memcpy_payload_identity plus ordinary gates; R1.1 also
requires each requested ideal_gates entry. R0.1 recovery/main experiments must
not wait for Lane4, TVD or RO. Lane4 does no build/simulation under the current
48GiB disk floor; it neither cleans others' files nor reduces the floor.

The runner now checks latest *published* Lane5 APPLICATION_ACCEPTANCE and
SCIENTIFIC_HOLD authority, and requires actual normalized qualification bytes
to match the latest published file. Fixed withdrawn source/binary identities
cannot retroactively acquire a source repair. Old prepared specs are rejected
before registry claim or child launch, even if they retain an earlier PASS.
A repaired qualification also needs both explicit production repair gates,
unchanged evidence bytes and per-mode ideal qualification. Same-binary matched
baseline/config/trace/epoch/vector checks remain. V1 RO-off and explicit V2
RO-off vectors are supported without projecting or rekeying the identity.

Execution normality and scientific acceptance are separate. New diagnostic
execution results remain PENDING_LANE5_CURRENT_ACCEPTANCE until authoritative
CURRENT_ACCEPTED matches the exact key/source/binary/config/trace/raw hash.
Later withdrawal has veto; missing or ambiguous acceptance fails closed.
No preserved COMPLETE_VALID record is rewritten. Eligibility to launch a new
repaired release does not itself accept any result.

Lane5 is editing its runner during repair recovery. The loader consumes the
exact runner_source_commit/runner_sha256 from CLIENT_CONTRACT, freezes only
run.py/validate.py/feature_schema.py bytes from Git in a small Lane4 tool cache,
and keeps the original hash-checked Lane5 registry module, lock and authority.
It does not import unpublished working-tree runner edits or fork the registry.
Lane5's current runner already fixes whole-file multiline config lexing; the
previous temporary lexer callback replacement has been removed.

Source audit replay of Lane5's combined clock/warmup candidate on exact old
R1 and Lane4 candidate is static-only. A separate one-call candidate patch
restores memcpy offset for ideal resident Tag replacement time while retaining
physical bank/response time. It is not compiled or qualified. Dirty victim
loss, post-producer rewarm/reference reset, partial sectors and Tag/slot commit
agreement remain explicit production audit items for Lane1's official repair.
Do not treat a successful patch apply or I_READ_HIT bypass as a warmup PASS.

R1.1 formal cells remain NOT_RUN until exact repaired source/binary qualification
and same-R1.1-binary B16 specs exist. No I_BANK or expanded matrix is introduced.
