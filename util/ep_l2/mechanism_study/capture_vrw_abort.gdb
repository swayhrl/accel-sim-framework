set pagination off
set confirm off
set print elements 6
set print repeats 4
set max-value-size 131072
set disable-randomization off
set index-cache enabled off
set history save off
handle SIGABRT stop print nopass
run
python
import gdb
f = gdb.newest_frame()
while f is not None:
    name = f.name() or ""
    if "submit_ro" in name or name == "main":
        f.select()
        sal = f.find_sal()
        gdb.write("VRW_FRAME|function=%s|line=%s\n" % (name, sal.line))
        for key in ("line", "full", "before"):
            try:
                gdb.write("VRW_LOCAL|%s=%s\n" % (key, f.read_var(key)))
            except Exception as e:
                gdb.write("VRW_LOCAL_UNAVAILABLE|%s|%s\n" % (key, e))
        if "submit_ro" in name:
            try:
                obj = f.read_var("this").dereference()
                for key in ("ro_packets", "ro_bytes", "full_uid"):
                    gdb.write("VRW_STATE|%s=%s\n" % (key, obj[key]))
                runtime = obj["f"]["cache"].dereference()["m_ro"].dereference()
                owner = runtime["tx"]
                pointer = gdb.lookup_type("ep_l2_ro::transactions").pointer()
                if owner.type.sizeof != pointer.sizeof:
                    raise RuntimeError("unique_ptr layout not one pointer; skip raw ABI inspection")
                tx = owner.address.cast(pointer.pointer()).dereference().dereference()
                slots = tx["m_slots"]["_M_impl"]
                start, finish = slots["_M_start"], slots["_M_finish"]
                count = int(finish-start)
                if count < 1 or count > 1168:
                    raise RuntimeError("unexpected transaction slot count")
                for i in range(count):
                    e = start[i]
                    if bool(e["live"]) and int(e["line"]) == 0x400000:
                        waiters = e["waiters"]["_M_impl"]
                        n = int(waiters["_M_finish"]-waiters["_M_start"])
                        gdb.write("VRW_A0|slot=%u|attached=%u|reuse_seen=%u|required=%u|issued=%u|ready=%u|waiters=%u\n" %
                            (i,int(e["attached"]),int(e["reuse_seen"]),int(e["required"]),
                             int(e["issued"]),int(e["ready"]),n))
            except Exception as e:
                gdb.write("VRW_STATE_UNAVAILABLE|%s\n" % e)
    f = f.older()
end
bt 14
quit
