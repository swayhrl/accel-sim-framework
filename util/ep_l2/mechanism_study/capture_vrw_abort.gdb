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
            except Exception as e:
                gdb.write("VRW_STATE_UNAVAILABLE|%s\n" % e)
    f = f.older()
end
bt 14
quit
