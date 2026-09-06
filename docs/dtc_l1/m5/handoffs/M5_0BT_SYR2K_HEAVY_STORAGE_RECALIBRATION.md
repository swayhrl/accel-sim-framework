# M5.0BT — SYR2K heavy storage recalibration

Status: **ACTIVE — SERIAL_STREAMING_ADMISSION_REPLACES_2DCONV_UPPER_BOUND**

This is an operational storage-policy correction authorized for the current
capture host. It changes no workload, source, input, tracer, formal platform,
or result identity.

## Observed exact SYR2K high-watermark

| component | bytes | measurement |
| --- | ---: | --- |
| raw trace set | 33,855,308,862 | complete immutable bundle |
| grouped traceg set | 23,839,620,990 | complete immutable bundle |
| immutable working bundle | 57,694,970,930 | sum of all immutable bundle files |
| transfer archive | 3,804,351,548 | archived syr2k.tar.zst |
| surviving tracer scratch | 17,276,879 | capture-root scratch-tracer after completion |
| reconstructed complete peak footprint | 61,516,599,357 | bundle + archive + measurable scratch |

The historical peak of transient directories that were moved into the immutable
bundle cannot be independently reconstructed after finalization. The complete
bundle is therefore used rather than a partial raw/grouped proxy. The
reconstructed footprint includes all retained raw and grouped traces, checker
and build files, the concurrently created archive, and all surviving measurable
scratch.

## Recalibrated fail-closed admission

The previous 2DConv receipt used
2,767,658,899 * 10 * 2 = 55,353,177,980 bytes. SYR2K's single bundle is
57,694,970,930 bytes, so that prior aggregate projection is not an empirical
upper bound and must not admit future heavy captures.

The capture policy is now researcher-authorized **serial streaming offload**:

capture -> checker/bundle/archive PASS -> copyback/local immutable PASS ->
proof-bound remote working-bundle eviction -> next capture.

For one new capture the controller requires live free space at least equal to
the maximum measured complete capture footprint:

61,516,599,357 bytes.

The prior factor of 20 encoded ten retained Paper bundles times a twofold
reserve. It is not retained under the explicitly authorized streaming policy:
retaining ten uncompressed bundles is now forbidden. The replacement head is
the whole measured single-capture peak, including its archive and measurable
scratch, and controller safety_factor=1 therefore does not discard any
measured component. Existing free space beyond that threshold is residual
headroom; a controller never starts a capture below the threshold.

At the pre-SYR2K-eviction observation, 34,716,172,288 free bytes correctly
fails this gate. After proof-bound SYR2K bundle eviction, the nominal free
space is 92,411,164,259 bytes, leaving 30,894,564,902 bytes above the new
threshold before any subsequent capture writes. Every launch remeasures live
free bytes; these are not a promise that an unmeasured workload fits.

## Consequences

- **SpMV** remains next and is admitted only after SYR2K local immutable PASS,
  proof-bound eviction, and a fresh live gate PASS.
- **2MM** is HEAVY_SIZE_UNKNOWN: frozen NI=NJ=NK=NL=1024, two dense
  multiplication phases, no downsizing. It needs the recalibrated gate plus
  pre-identified proof-bound eviction candidates before launch.
- Every Extended-20 capture uses this same floor until it establishes a larger
  measured footprint. If any workload exceeds SYR2K, its exact whole footprint
  becomes the new maximum for all following captures.
- The remote archive and compact provenance are retained. Only a redundant
  working bundle may be removed through --evict-offloaded after the exact
  local immutable receipt binds archive SHA, bundle ID and SHA256SUMS.
