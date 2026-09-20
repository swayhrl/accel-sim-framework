# Node164 mount diagnosis — 174-new

Status: `INFRASTRUCTURE_BLOCKED`

Date: 2026-09-20

Mode: `ZERO SCIENCE`. No simulator was run and no scientific data was generated.

## Discovered mount mechanism

- mountpoint: `/root/share/mnt164`
- source: `admin-wcx@10.208.130.164:/home/shared`
- filesystem: `fuse.sshfs`
- options: `rw,nosuid,nodev,relatime,user_id=0,group_id=0,allow_other`
- required endpoint: host `10.208.130.164`, account `admin-wcx`, port `22`.

`findmnt` and `/proc/mounts` showed that sshfs mapping, but reads under
`/root/share/mnt164/huangrulin` failed with `Transport endpoint is not connected`.

## Authority and process checks

- No live sshfs/rclone/gocryptfs/NFS/mount process owned this mount.
- No fstab or systemd mount authority references this mountpoint. PID 1 is not systemd.
- Shell history has prior mount *usage*, but no trusted original sshfs remount command or config.
- `/root/.ssh/config` has only a gpu109 host entry; no node164 identity/config exists.
- The only local private identity file is `id_ed25519_gpu109`, publicly labeled
  `hrl-174-new-to-gpu109`; it is not node164 mount authority.
- `ssh-add -L` reported no accessible SSH agent.

## Safe stale-endpoint handling

After confirming no live mount process or writer, the stale endpoint was detached with:

```bash
fusermount3 -uz /root/share/mnt164
```

The path is now an ordinary empty directory rather than a mountpoint.
