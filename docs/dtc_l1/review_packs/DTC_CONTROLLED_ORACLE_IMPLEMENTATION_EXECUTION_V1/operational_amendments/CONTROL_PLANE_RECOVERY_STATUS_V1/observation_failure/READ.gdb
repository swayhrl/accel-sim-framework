set pagination off
set confirm off
set auto-load python-scripts off
set scheduler-locking off
python
_ts=[t for t in gdb.selected_inferior().threads() if t.ptid[1]==1498278]
if len(_ts)!=1:raise gdb.GdbError('exact Main LWP missing')
_ts[0].switch()
end
set $rv_buf=(void*)mmap((void*)0,4096,3,34,-1,0)
restore /root/data/dtc_controlled_oracle_20261106_v1/control/owner_recovery_readonly_verification_v1/PAYLOAD.bin binary $rv_buf
set $rv_gil=(int)PyGILState_Ensure()
set $rv_run=(int)PyRun_SimpleString((char*)$rv_buf)
call ((void(*)(int))PyGILState_Release)($rv_gil)
printf "ORACLE_RECOVERY_READONLY_RUN=%d\n",$rv_run
detach
quit
