# New contract V2 finite hand-written schedule, not inherited old Python PASS.
# Registered ingress takes one tick; READ then COMMIT; cancel consumes READ;
# each count write (even net0) occupies the single count lane.
import csv,json,pathlib
q=pathlib.Path(__file__).parent
expected=[
("enqueue_plus1",0,1,0,0,0,0,0,0),
("read_plus1",1,1,1,1,0,0,0,0),
("commit_plus1",2,0,0,1,1,0,1,1),
("enqueue_net0",3,1,0,1,1,0,1,1),
("read_net0",4,1,1,2,1,0,1,1),
("commit_net0",5,0,0,2,2,0,1,2),
("read_cancel",7,1,1,3,2,0,1,2),
("cancel",7,0,0,3,2,1,1,2),
("enqueue_after_cancel",7,1,0,3,2,1,1,2),
("new_read_no_refund",8,1,1,4,2,1,1,2),
("commit_plus1_after_cancel",9,0,0,4,3,1,2,3),
("cleanup128",393,0,0,132,131,1,0,5),
("k2_shared_old_read",1,2,2,1,0,0,0,0),
("k2_first_count_write",2,1,1,1,1,0,1,1),
("k2_counter_busy_no_refund",2,1,1,1,1,0,1,1),
("k2_second_serial_count_write",3,0,0,1,2,0,2,2)]
with (q/"CONTRACT_EVENT_TRACE_V2.csv").open() as f:
 rows=list(csv.reader(f))[1:]
got=[tuple([r[0]]+[int(x) for x in r[1:]])for r in rows]
assert got==expected,(got,expected)
r={"PASS":True,"contract":"NEW_V2_REGISTERED_READ_COMMIT_SINGLECOUNT","compared_snapshots":len(got),
 "net0_writes":1,"cancel_read_refund":False,"cleanup_empty_rows_paid":128,"cleanup_ticks":384,
 "k2_stale_revalidate_count_busy_serial_commit":True,"application_qualification":False}
(q/"PYTHON_PRODUCTION_EVENT_COMPARE_V2.json").write_text(json.dumps(r,indent=2)+"\n")
print(json.dumps(r))
