def guard_only(case):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'native sole entry required')
    route = read(ROOT / 'control/NATIVE_ENTRY_ROUTE.json')
    need(route['goal'] == GOAL and route['status'] == 'MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE', 'native route qualification missing')
    prior = P(route['prior_entry_ref']['path']).read_bytes()
    need(sha(route['prior_entry_ref']['path']) == route['prior_entry_ref']['sha256'], 'prior native entry evidence changed')
    entry = route['entry_ref']
    (registry, _) = authority()
    need(registry['registered_future_requests'][GOAL]['native_entry_ref'] == entry, 'entry outside registered scoped sole-entry')
    need(P(entry['path']) == ROOT.parent / 'bin/native' and sha(entry['path']) == entry['sha256'], 'scoped native entry path/content drift')
    need((NATIVE / 'bin/native').read_bytes() == prior, 'foreign global native bytes changed; requalification required')
    current = P(entry['path']).read_bytes()
    need(current.endswith(prior) and route['own_prelude'].encode() in current, 'native route or peer suffix changed')
