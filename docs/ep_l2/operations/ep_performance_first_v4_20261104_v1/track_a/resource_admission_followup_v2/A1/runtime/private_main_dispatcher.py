# Main-only private claim carrier; no import-time actions.
import ep_perf_native_wv_modes_draft as engine
def claim(case,binding):
    # Both schema and fresh request2 authorization precede locks or claim writes.
    s=engine.preclaim_schema(case,binding)
    engine.spec_for(case)
    with engine.locked(engine.GLOBAL_MAIN_ADMISSION_LOCK):
        path=engine.ROOT/'control/DISPATCH_CLAIMS.json'
        carrier=engine.read(path)if path.exists()else dict(claims={})
        engine.need(case not in carrier['claims'],'claim already exists; no retry')
        carrier['claims'][case]=dict(state='CLAIMED',spec_sha256=engine.sha(engine.spec_path(case)),host_cpu=binding['host_cpu'],estimated_peak_RAM_bytes=s['estimated_peak_RAM_bytes'],remaining_write_bytes=s['limits']['result_bytes'])
        engine.put(path,carrier)
    return dict(status='EXACT_UNSPENT_CLAIM_CREATED',cohort=case)
