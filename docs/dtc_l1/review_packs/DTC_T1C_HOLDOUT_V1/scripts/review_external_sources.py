"""Read-only project identity audit; does not alter the running authority or gates."""
from common import *


def main():
    target=ROOT/'EXTERNAL_RESOURCE_IDENTITIES.json'
    previous=json.loads(target.read_text()) if target.exists() else {}
    identities=previous.get('identities',{})
    authority=json.loads((ROOT/'AUTHORITY_ACTIVE.json').read_text())
    prefixes=('/workspace/results/ep_l2_ft20261016/',
              '/workspace/ep_l2_potential20261017_lane5_results/')
    expected='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee'
    unknown=[];samples=0
    for line in (ROOT/'RESOURCE_SAMPLES.jsonl').read_text().splitlines():
        snapshot=json.loads(line);samples+=1
        for item in snapshot['processes']+snapshot.get('unrelated_project_processes',[]):
            argv=item['argv']
            if item['pid']==authority['pid'] and item['start_ticks']==authority['start_ticks']:continue
            if argv and argv[0].startswith(str(ROOT/'attempts/binaries')+'/'):continue
            key=str(item['pid'])+':'+str(item['start_ticks'])
            if key in identities:continue
            binary=Path(argv[0]) if argv else None
            if not argv or not argv[0].startswith(prefixes) or binary.name!='accel-sim.out':
                unknown.append(dict(sample_utc=snapshot['utc'],process=item));continue
            configs=[Path(argv[i+1]) for i,arg in enumerate(argv) if arg=='-config']
            try:
                digest=sha(binary)
                text='\n'.join(p.read_text() for p in configs)
                valid=(digest==expected and configs and all(p.parent==binary.parent for p in configs)
                    and '-gpgpu_ep_l2_ft_mode ' in text
                    and not any(line.lstrip().startswith('-gpgpu_dtc') for line in text.splitlines()))
                assert valid,'Binary/config outside verified independent EP-L2 identity'
                identities[key]=dict(first_observed_utc=snapshot['utc'],pid=item['pid'],
                    start_ticks=item['start_ticks'],binary=str(binary),binary_sha256=digest,
                    configs=[dict(path=str(p),sha256=sha(p)) for p in configs],
                    status='INDEPENDENT_EP_L2_NO_DTC_CONFIG')
            except (OSError,AssertionError) as exc:
                unknown.append(dict(sample_utc=snapshot['utc'],process=item,error=str(exc)))
    record=dict(utc=now(),status='PASS_ALL_SAMPLED_FOREIGN_PROCESSES_IDENTIFIED' if not unknown else 'UNRESOLVED_FOREIGN_IDENTITY_REQUIRES_REVIEW',
        samples_reviewed=samples,identities=identities,unresolved=unknown,
        running_wrapper_modified=False,gate_or_timeout_modified=False,performance_read=False,
        global_resource_limits_unchanged=True)
    tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(target)
    print(record['status'],'samples',samples,'distinct independent foreign processes',len(identities),'unresolved',len(unknown))
    assert not unknown,'Review foreign identity; never override a resource or scientific gate'


if __name__=='__main__':main()
