"""CPU sizeof disclosure only; never builds or starts a model executable."""
from common import *


def main():
    source=PACK/'tools/host_layout_probe.cc';rows=[]
    for label,core,commit in [('X2',BUILD/'x2-source',X2),
                              ('AG3',CORE,'c8090115bd57512b1b23fca7d925301fa620c751')]:
        dest=BUILD/('ag3-cpu-host-layout-'+label.lower())
        argv=['nice','-n','19','/usr/bin/g++','-std=gnu++17','-fno-access-control',
              '-I'+str(core/'src'),str(source),'-o',str(dest)]
        run=subprocess.run(argv,capture_output=True,text=True)
        (RAW/('host-layout-'+label+'.cxx17.compile.stderr')).write_text(run.stderr)
        run.check_returncode()
        result=subprocess.run([str(dest)],capture_output=True,text=True);result.check_returncode()
        (RAW/('host-layout-'+label+'.stdout')).write_text(result.stdout)
        values={k:int(v) for k,v in (item.split('=') for item in result.stdout.split())}
        rows.append(dict(label=label,core=commit,header_sha256=sha(core/'src/gpgpu-sim/dtc-l1-common.h'),compile_argv=argv,executable=str(dest),executable_sha256=sha(dest),values=values))
    a,b=[r['values'] for r in rows];delta={k:b[k]-a[k] for k in a}
    report=dict(status='PASS_CPU_SIZEOF_ONLY_NO_MODEL_OR_TRACE',rows=rows,delta_bytes=delta,
                header_persistent_delta_formula='640*delta_physical_line+128*delta_entry+delta_frontend',
                configured640physical128PIB_header_object_size_delta_at_full_occupancy_bytes_per_SM=640*delta['physical_line']+128*delta['entry']+delta['frontend'],
                excludes=['allocator/list/vector dynamic storage','LDST object delta not remeasured by this header-only probe','temporary assertion structures','payload banks','RTL area/timing/power'],
                source_sha256=sha(source),actual_simulator_starts_by_this_probe=0,
                engineering_failure=dict(reason='initial sizeof probe incorrectly requested C++11; production compile_commands uses gnu++17; no production source change',stderr=str(RAW/'host-layout-X2.compile.stderr'),stderr_sha256=sha(RAW/'host-layout-X2.compile.stderr')))
    write(PACK/'HOST_LAYOUT_DISCLOSURE.json',report);print(json.dumps(report))


if __name__=='__main__':main()
