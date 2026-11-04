# V8 executable and analysis provenance

- supervisor.py dispatches BASE then PREFIX under the single common-lock interval.
- worker.py implements the frozen V8 configurations;capture.py,numeric_observation.py and local_observer.py implement pre-gate evidence and separated observations.
- resource_monitor.py,rss_lifecycle.py,desktop_policy.py,shared_gate.py retain V7 safety scope;the dispatcher uses serial workers.
- postrun_v8_analysis.py is the executed independent CPU performance/numeric/cache analysis and reads either an original resource receipt or its exact gzip archive.
- postrun_observer_analysis.py is the executed CPU tensor analysis,including documented internal/external request-ID mapping.
- Older inherited analyze.py,independent_analysis.py and postrun_analysis.py are provenance copies;they were not invoked for V8 results. Use the two V8 analyses above.
- No command in this archive grants permission to rerunGPU;the Goal is closed after publication.

After CPU analyses,pack_derived_evidence.py recreates deterministic gzip/index packaging for large derived numeric tables;all rows remain byte-exact in the archive.
