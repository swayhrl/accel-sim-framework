"""Archive terminal resource evidence only; never launch or change a pilot point."""
from common import *


def time_values(path):
    text = path.read_text()
    fields = {}
    for key, pattern in {
        'user_seconds': r'User time \(seconds\):\s*([\d.]+)',
        'system_seconds': r'System time \(seconds\):\s*([\d.]+)',
        'cpu_percent': r'Percent of CPU this job got:\s*(\S+)',
        'elapsed_wall': r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)',
        'max_rss_kib': r'Maximum resident set size \(kbytes\):\s*(\d+)',
    }.items():
        match = re.search(pattern, text)
        fields[key] = match.group(1) if match else 'UNAVAILABLE'
    return fields


def main():
    terminal = json.loads((ROOT/'AUTHORITY_TERMINAL.json').read_text())
    assert terminal['status'] == 'NATURAL_FOREGROUND_AUTHORITY_END'
    assert not terminal['final']['active'], 'No resource publication while a point is active'
    authority = json.loads((ROOT/'AUTHORITY_ACTIVE_V2.json').read_text())
    live = proc(authority['pid'])
    assert not live or live['state'] == 'Z' or live['start_ticks'] != authority['start_ticks']
    with (PACK/'PRE_REGISTRATION.tsv').open() as stream:
        plan = list(csv.DictReader(stream, delimiter='\t'))
    rows = []
    for point in plan:
        run = ROOT/'attempts'/(point['label']+'_'+point['attempt_uuid'])
        timefile = run/'resource.time'
        launched = (run/'RUN_START.json').exists()
        assert not launched or (run/'RUN_TERMINAL.json').exists(), str(run)
        rows.append(dict(
            candidate=point['candidate'], workload=point['workload'],
            attempt_uuid=point['attempt_uuid'], launched=launched,
            **(time_values(timefile) if timefile.exists() else {
                key: 'UNAVAILABLE' if launched else 'NOT_LAUNCHED'
                for key in ['user_seconds', 'system_seconds', 'cpu_percent',
                            'elapsed_wall', 'max_rss_kib']}),
            resource_time_path=str(timefile),
            resource_time_sha256=sha(timefile) if timefile.exists() else '',
        ))
    samplefile = ROOT/'RESOURCE_SAMPLES.jsonl'
    samples = [json.loads(line) for line in samplefile.read_text().splitlines() if line]
    assert samples and all(s['host'] == 'huangrulin-174' for s in samples)
    times = [datetime.fromisoformat(s['utc']) for s in samples]
    assert times == sorted(times)
    def headroom(s):
        limit = s['cgroup_memory_max']
        return limit-s['cgroup_memory_current'] if limit is not None else s['mem_available']
    def own_simulators(s):
        return [p for p in s['processes'] if p['argv'] and
                p['argv'][0].startswith(str(ROOT/'attempts/binaries')+'/') and
                p['argv'][0].endswith('/accel-sim.out')]
    maximum_concurrency = max(len(own_simulators(s)) for s in samples)
    assert maximum_concurrency <= 2
    counters = {}
    for name in ['pswpin', 'pswpout', 'cgroup_swap_current']:
        values = [s[name] for s in samples]
        counters[name] = dict(first=values[0], last=values[-1], minimum=min(values),
                              maximum=max(values), last_minus_first=values[-1]-values[0])
    events = {}
    for name in sorted(samples[0]['cgroup_events']):
        values = [int(s['cgroup_events'][name]) for s in samples]
        events[name] = dict(first=values[0], last=values[-1],
                            maximum_minus_first=max(values)-values[0],
                            monotonic=all(a <= b for a, b in zip(values, values[1:])))
    summary = dict(
        utc=now(), authority_terminal_sha256=sha(ROOT/'AUTHORITY_TERMINAL.json'),
        samples_path=str(samplefile), samples_sha256=sha(samplefile),
        sample_count=len(samples), first_sample_utc=samples[0]['utc'],
        last_sample_utc=samples[-1]['utc'],
        largest_sample_gap_seconds=max((b-a).total_seconds() for a,b in zip(times,times[1:]))
        if len(times)>1 else None,
        minimum_host_MemAvailable_bytes=min(s['mem_available'] for s in samples),
        minimum_cgroup_headroom_bytes=min(headroom(s) for s in samples),
        minimum_disk_free_bytes=min(s['disk_free'] for s in samples),
        maximum_own_sampled_simulator_concurrency=maximum_concurrency,
        maximum_own_sampled_sum_rss_kib=max(sum(p['rss_kib'] for p in own_simulators(s)) for s in samples),
        maximum_memory_full_psi_avg10=max(float(s['pressure']['memory']['full']['avg10']) for s in samples),
        maximum_io_full_psi_avg10=max(float(s['pressure']['io']['full']['avg10']) for s in samples),
        samples_with_unrelated_project_processes=sum(bool(s.get('unrelated_project_processes')) for s in samples),
        samples_with_owned_old_lane_locks=sum(any(p['owners'] for p in s['old_locks']) for s in samples),
        counters=counters, cgroup_events=events,
        limitations=[
            'Host/cgroup counters and pressure include all projects; changes are not attributed to DTC.',
            'Minute samples do not prove absence of transients between samples.',
            'Sampled concurrent RSS is not the sum of independently measured per-point peak RSS.',
            'resource.time is the attempt time-v scope; missing fields remain UNAVAILABLE.',
            'These are CPU simulator resource costs, not synthesized hardware area, power or timing.',
        ],
    )
    table(PACK/'EXECUTION_RESOURCES.tsv', rows)
    write(PACK/'RESOURCE_EXECUTION_SUMMARY.json', summary)
    print('Terminal resource archive:', len(rows), 'registered points;', len(samples), 'global samples')


if __name__ == '__main__':
    main()
