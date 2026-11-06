set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
python
_matches=[t for t in gdb.selected_inferior().threads() if t.ptid[1]==1498278]
if len(_matches)!=1:raise gdb.GdbError('exact Main LWP missing')
_matches[0].switch()
end
set $oraclebuf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore /root/data/dtc_controlled_oracle_20261106_v1/control/initial_science_main_bootstrap_v1/PAYLOAD.bin binary $oraclebuf
set $oraclegil=(int)PyGILState_Ensure()
set $oraclerun=(int)PyRun_SimpleString((char*)$oraclebuf)
call ((void(*)(int))PyGILState_Release)($oraclegil)
printf "ORACLE_INITIAL_SCIENCE_GIL=%d RUN=%d\n",$oraclegil,$oraclerun
detach
quit
