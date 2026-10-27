# Standalone engineering original-full tree recovery

restore_original_full.py SHAeb94da0680b1e20c86dcb737207b3067a758351bf041274d51fcf88943ad8143. Linux/Python3.9+, standard library and readonly findmnt only; no runtime, actor, simulator, authority/registry or model imports. The helper writes only one fresh destination and emits its receipt to stdout. Main supplies current shared-resource admission, CPU/AS/wall limits, and separately calls two independent Python processes from the two independently restored native parcels.

    python3 -I restore_original_full.py --parcel FIRST_PARCEL --destination FRESH_NATIVE_TREE --max-bytes EXACT_BOUND --inventory-sha256 TRUSTED_INVENTORY_SHA --archive-sha256 TRUSTED_COMPRESSED_SHA

All five arguments are mandatory. Main obtains expected inventory/archive SHA256 from the fixed technical-negative disposition/two stream-verification receipts and cross-checks them against the real NAS parcel manifest. The helper never turns its own freshly computed hash into an expected value. Omitted/wrong hashes reject before target creation. Parcel files are ORIGINAL_CONTENTS.json and ORIGINAL_RESULT.tar.gz; inventory<=8MiB and compressed input<=32MiB.

EXACT_BOUND is computed from the actual trusted inventory, with every directory including root counted once:

    sum(ceil(file.size /4096)*4096 for each file) +4096*directory_count +65536

The supplied --max-bytes must equal that value, not an arbitrary larger allowance. Both final logical file bytes and actual filesystem allocated bytes must remain below it. This is an ENGINEERING_ONLY original-full recovery cap. It does not change the original scientific96MiB cap or NOT_ACCEPTED_RESOURCE_ENVELOPE. The inventory must explicitly say original_case_resource_qualified=false, original_cap_bytes=100663296 and reported original allocation above that cap. Synthetic controls explicitly label that allocation declaration as mock data; they are not actual DWT evidence.

Safety and content:

- Canonical relative inventory paths only; direct input/destination paths; reject traversal, duplicate paths, undeclared parents, missing root, symlink/hardlink/special/sparse TAR entries, incorrect order/size/metadata and extra/trailing nonzero content.
- Existing targets are never reused/overwritten; destination parent must already exist on ext4. Input/output ancestor symlinks reject. Destination cannot be inside the original source tree or parcel, and cannot enclose either.
- Directories are created privately first. File writes use dir_fd traversal with O_DIRECTORY/O_NOFOLLOW and O_CREAT/O_EXCL/O_NOFOLLOW; writes are bounded by declared sizes and the engineering cap.
- Every file is streamed, checked against the complete inventory SHA, fsynced, chowned/chmodded and given exact nanosecond mtime. Directories receive metadata in reverse depth order after all content is written.
- Reopened target files and the exact complete target inventory are verified again, including type/size/fullSHA/mode/UID/GID/mtime_ns and allocated/logical totals. Gzip EOF/CRC and tar padding are fully consumed. Input parcel SHA values are checked again at the end.
- Failure returns nonzero and preserves all partial destination bytes for inspection. No deletion, automatic retry, scientific acceptance or budget operation occurs. Successful receipt is ENGINEERING_ONLY_ORIGINAL_CASE_FAILED96M_ORIGINAL_FULL_NATIVE_RESTORE_PASS; keep stdout outside the recovered tree to preserve exact inventory.

Main must retain the original failed case status and historical C3 point. Actual DWT original-full restoration has NOT been executed by Agent B. Main's two actual engineering targets may exceed96MiB under their derived bounds; that is valid engineering recovery evidence, never retroactive scientific qualification. No numeric-SASS, input capture completeness or performance claim is supplied.

Executed controls: engineering_runs/32dd4dd5-3dbb-4804-92e9-bb22f22e7bf0/SYNTHETIC_SECURITY_RESULT.json SHAe830d4e438a9c9db4df7a0c80d0360a01d2e1949c98cd2c6a967cbdfc39b2f08;27controlsPASS in1.30s, CPU19/nice10/AS512MiB/wall120, local allocation520192B<8MiB. Includes two actual independent synthetic subprocess restorations and metadata/hash equality, plus negative traversal/absolute/backslash/duplicate inventory, TAR soft/hard links/FIFO/device, wrong expected hashes, too-large/small max, corrupt file data/nsmtime, truncatedgzip, hidden trailing data, missing TAR file, symlink inputs/outputs, input hardlink, source/parcel overlap and existing output. Resource admission was sampled before tests with ATAX model live on its own slot. No actual DWT parcel/fulltree, NAS, Source, model or registry was touched.
