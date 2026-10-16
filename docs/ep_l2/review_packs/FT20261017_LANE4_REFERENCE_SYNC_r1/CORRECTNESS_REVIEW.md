# Selected-sector reference synchronization

## Semantics retained from exact c948

The accepted host operation initializes all bytes of its one selected32B sector
as unknown version-zero symbols. It is an untimed prefill, not a numeric zero
store or free bank service. The pre-existing clean/drained/index/generation
checks and full-width/partial-endpoint caller remain unchanged. Later
clean/quiescent prefill remains supported; no initial-only oracle restriction
was introduced.

The reference hook executes only after ft_try_force_tag_access succeeds, before
the existing offset increment, and only when I_READ_HIT is enabled. Dirty,
pending, response-held and invalid-mask refusal exits precede it. Expanding the
already validated sector mask into byte positions matches the Payload write.

ReferenceMemory::host_prefill changes selected versions to0 and erases their
old known-value labels. It never resets next_version_, versions of other bytes,
other lines or pre-existing response snapshots. This is host-write reference
maintenance within the accepted c948 semantics, not a new memory oracle.
Absence of a versions_ entry already means version0, so no new entry is needed
on a cold prefill. Real later GPU producers continue to advance the same
monotonic version counter.

## Counterexample and regression sources

The partition regression uses real partition/response/lower paths, not a mock
call to ReferenceMemory::write. Its intended sequence is:

| Stage | Expected reference and physical behavior |
|---|---|
| Prefill A sector0/1 | Unknown version0, no timed bank grant |
| GPU store A sector0, consume response | Known producer bytes91, version>0 |
| Attempt dirty same-line prefill | Refuse; reference/offset/grants unchanged |
| Ordinary L1 write-allocation read at conflicting line | Actual dirty-A WB, staging/lower acceptance, clean new victim; all drain |
| Later prefill A sector1 | Accept; preserve sector0's old producer reference |
| Later prefill A sector0 | Accept; replace sector0 with unknown version0 |
| Repeated prefill | Same selected-sector symbols; no global reset |
| Hold real read response | Refuse prefill, preserve response snapshot |
| Read untouched sector2 | Preserve its independent known seed17 |

The old ideal implementation has no hook at the second accepted sector0
prefill, so its reference retains producer version/known bytes although the
Payload initialization is version0. The new source includes the missing hook.
The expected distinguishing assertion is unknown(read(A)) after that later
prefill. This is an analytically identified counterexample and a prepared
regression; **neither old-red nor new-green execution was performed**.

The header regression separately checks selected32B reset, unchanged other
bytes, copy snapshot preservation, repeated reset, later monotonic producer
versions, fresh-map behavior and no high-address alias. It is also NOT_RUN.

The test config is explicit static B16/WBUF16, one set/one way to force real
dirty eviction, one-cycle bank budget inherited from the producer, a real ROP
delay and one-entry response queue. It is a directed test geometry, not a new
application configuration or performance measurement.

## Remaining production work, not skipped qualification

Official R0.1 has priority. After the actual official parent and separate R1.1
runtime are published, rebind or replay the source delta to their precise
identities, compile these two new cases through the existing guarded production
test driver and run affected ideal/WB/metadata/partition regressions. Observe
real physical bank grant limits, memcpy-offset Tag time, dirty refusal,
WB/set_done and complete request/response closure. Lane5 independently qualifies
repair and applicable ideal modes on the exact new binary before application
use. No source-only check here satisfies those production gates.

Unchanged qualification/runner tests were not repeated. The local shared client
transition is recorded in VALIDATION; a current coherent registry hash and
native V2 authority check remain mandatory, with no fallback to old certificates.
