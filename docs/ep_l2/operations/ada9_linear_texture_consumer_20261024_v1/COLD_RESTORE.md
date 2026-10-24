# ADA9 native evidence cold closure

True164 object: /root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1/objects/stage_evidence_ada9_native_consumer_174new_20261024_v1

The regular tar contains205 files and111099493 regular bytes. payload.tar is111472640 bytes, SHA afd70bbd3af62d16aa9d70ccf6719b08545e46ba82bb2d41d4019250726af0a3. MANIFEST.json SHA is42eee19d6d9cec1884fa8d1a8a07c40b85c65fccff656147e773a6f443009dc4. COMMIT.json SHA is26ed2c9a00f0679c56d5b03ab8e0c99ec5bfe716474a4e12588e5825f20a9551.

The archive was closed and reopened, all205 members rehashed against the source manifest, and its full archive SHA recorded before COMMIT. Native SOURCE→TARGET→109-local-IO locks were held in that order for14.28 seconds and fully released. The source remains present; zero local bytes were released. This object is engineering evidence, not a formal workload catalog entry.

After safe regular-member-only tar extraction into a fresh local directory, its root is174new/ada9_native_result_engineering_pack_20261024_v1. FROZEN_PATH_MAP.json binds174 immutable exact-spec absolute paths to126 deduplicated blobs. Native result/control/config/epoch-registry history reside in native_root/. Native executable and every sampled actual dependency are in pinned_blobs/ and the mapping preserves their SHA, byte size and numeric mode. Producer source/raw capsules/loaded cubin already pinned by the exact spec are present in the same blob set. consumer_evidence/ also includes accepted and failed candidate binaries, actual C++ CPU probes, source, logs and both Git bundles; parent_review/ includes independent parent review and verifier code.

To materialize the pin aliases without touching original paths, invoke the saved materialize_ada9_pins_v1.py with the extracted pack root and a new output directory. It verifies each unique blob and every metadata/path rule before creating OUTPUT/original/<absolute original path>, then rehashes every restored alias. Its CPU qualification restored all174 aliases /101401136 logical bytes from126 unique blobs without application execution. Parent cold restoration must independently start with true164 tar/member SHA, rather than treating this source-side qualification as a cold proof.

The archive does not retire the case8 native128MiB reservation. Parent independent cold readback and the existing registry CAS are required for that separate accounting change; eight consumed attempts must remain consumed.
