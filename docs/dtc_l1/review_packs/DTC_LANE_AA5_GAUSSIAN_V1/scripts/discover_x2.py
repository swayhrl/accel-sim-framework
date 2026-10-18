"""Read advertised refs only; no old Core substitution, mutation, or launch."""
from common import *
import sys

def main():
    label=sys.argv[1];records=[];found=[]
    for kind,repo,old in [('Framework',FW_REPO,'49fb5d1b62b6f2387abc2d568bc8ae7543dc0df4'),('Core',CORE_REPO,CANDIDATE_CORE)]:
        r=subprocess.run(['git','-C',str(repo),'ls-remote','origin'],capture_output=True,text=True);assert r.returncode==0,r.stderr
        dtc=[line for line in r.stdout.splitlines() if 'dtc' in line.lower() or 'lane-x' in line.lower()]
        candidates=[line for line in dtc if re.search(r'(lane[-_]x2|dtc.*(?:normal.*export|terminal.*export|telemetry.*export))',line,re.I)]
        oldref=[line for line in dtc if 'lane-x-' in line and '\trefs/heads/' in line]
        rec=dict(repository_kind=kind,repository=str(repo),argv=['git','ls-remote','origin'],returncode=r.returncode,utc=now(),advertised_DTC_refs=dtc,X2_candidate_refs=candidates,original_X_refs=oldref,scope='advertised remote refs; not a proof about unadvertised/private commits or other repositories')
        records.append(rec);found.extend(candidates)
    result=dict(utc=now(),status='X2_CANDIDATE_REF_REQUIRES_EXACT_RELEASE_AND_ARTIFACT_REVIEW' if found else 'NO_BINDABLE_X2_RELEASE_FOUND',records=records,new_Core_commit=None,new_Core_binary_sha256=None,new_libcudart_sha256=None,original_X_not_a_substitute=True,full_simulations_started=0)
    write(ROOT/f'X2_DISCOVERY_{label}.json',result)
    print(result['status'])

if __name__=='__main__':main()
