# CODEX RECOVER — 174 node164 Mount / Publication Blocker V1

Date: 2026-09-20

Mode:

`INFRASTRUCTURE RECOVERY ONLY / ZERO SCIENCE`

Node:

`174-new`

Stage:

`AWMA_174_NODE164_MOUNT_RECOVERY_V1`

Current blocker:

```text
/root/share/mnt164/huangrulin
-> Transport endpoint is not connected

10.208.130.164
-> network reachable

direct SSH
-> authentication rejected / no usable credential
```

The V4 publication cannot be legally reconstructed without the immutable node164 bundle.

## 1. Do not repeat publication audits

The blocker is already established.

Do not re-run Git tree scans in a loop.

Do not run simulation.

Do not regenerate scientific values from memory.

## 2. Identify the mount type and prior mount authority

Run read-only diagnostics:

```bash
set -o pipefail

findmnt -T /root/share/mnt164 -o TARGET,SOURCE,FSTYPE,OPTIONS || true
mountpoint /root/share/mnt164 || true
grep -F ' /root/share/mnt164 ' /proc/mounts || true
mount | grep -F '/root/share/mnt164' || true

ps -ef | grep -E '[s]shfs|[r]clone|[g]ocryptfs|[m]ount.*164|[n]fs' || true

grep -R --line-number --fixed-strings '/root/share/mnt164'   /etc/fstab /etc/systemd/system /usr/lib/systemd/system /root/.config 2>/dev/null || true

systemctl list-units --type=mount --all | grep -E 'mnt164|root-share' || true
systemctl list-unit-files | grep -E 'mnt164|root-share' || true

history | grep -E 'mnt164|10\.208\.130\.164|sshfs|mount' | tail -100 || true
```

Also inspect only non-secret SSH configuration:

```bash
ls -la /root/.ssh
sed -n '1,240p' /root/.ssh/config 2>/dev/null || true
ssh-add -L 2>/dev/null || true
```

Do not print private-key contents.

Produce:

`NODE164_MOUNT_DIAGNOSIS.md`

recording:

- mount type;
- source;
- prior mount mechanism;
- whether a systemd/fstab authority exists;
- whether an existing SSH agent/key identity appears usable.

## 3. Recover stale FUSE/sshfs mount when possible

If `findmnt` shows a FUSE/sshfs-like mount and it is stale:

1. confirm no process is actively writing through the mount;
2. detach the stale mount using the least disruptive valid command, e.g.:
   `fusermount3 -uz /root/share/mnt164`
   or the system's equivalent;
3. recreate the mount ONLY using an already-existing trusted mount command/config/systemd unit.

Do not invent new credentials.

Do not copy secret keys.

If the historical mount uses a key already present and readable by the correct account, test it noninteractively.

## 4. Recover NFS/system mount when applicable

If the mount is NFS or a normal system mount:

- use the existing fstab/systemd authority;
- clear only the stale mount state as needed;
- remount the exact configured source;
- do not change export/mount options unless required for restoration and already documented.

## 5. If credentials are the only blocker

If the prior mount mechanism is sshfs/SFTP and no usable existing credential/agent is available:

STOP infrastructure recovery with:

`BLOCKED_EXTERNAL_NODE164_CREDENTIAL_OR_MOUNT_AUTHORITY_REQUIRED`

Return exactly:

- mount type/source discovered;
- historical mount command/config location if found;
- account/host/port required;
- whether a public-key file exists locally;
- whether SSH agent has an identity;
- exact non-secret error;
- exact administrator/user action required.

Do not brute-force accounts/keys.

## 6. Mount recovery acceptance

Before touching publication:

Require all:

```bash
findmnt -T /root/share/mnt164
test -r /root/share/mnt164/huangrulin
ls -ld /root/share/mnt164/huangrulin
```

Then perform a read-only probe of the exact V4 durable root.

Do not modify node164 raw evidence.

Write:

`NODE164_MOUNT_RECOVERY_RECEIPT.json`

with:

- recovered_at_utc;
- mount source/type/options;
- read-only probe paths;
- status.

## 7. Resume V4 publication only after mount PASS

Once immutable evidence is readable, immediately continue:

`CODEX_REPAIR_174_V4_REMOTE_PUBLICATION_V2.md`

Do not start new simulation.

Required final state remains:

`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED_VERIFIED_V2`

## 8. Remote closeout

Publish the infrastructure-recovery/publication state under the existing stable 174 closeout/ref chain.

Apply:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

No 174 cross-target science begins until publication V2 is independently closed.
