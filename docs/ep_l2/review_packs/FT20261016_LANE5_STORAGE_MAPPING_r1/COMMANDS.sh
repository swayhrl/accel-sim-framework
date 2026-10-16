hostname
readlink /proc/self/ns/mnt
df -B1 -P /workspace
findmnt -T /workspace -o TARGET,SOURCE,FSTYPE,MAJ:MIN,FSROOT
stat -c '%d %i %n' /workspace
df -B1 -P /tmp /root/share 2>/dev/null || true
findmnt -T /root/share 2>/dev/null || true
