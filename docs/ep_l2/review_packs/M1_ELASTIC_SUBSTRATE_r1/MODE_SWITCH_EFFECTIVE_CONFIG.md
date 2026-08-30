# Effective mode/config contract

M1 is not a durable substrate feature switch.  The post-M1 baseline is the
accepted D512 resource configuration with:

```text
gpgpu_ep_l2_payload_policy = 0  # static
gpgpu_ep_l2_feature_unified_payload = 0
gpgpu_ep_l2_feature_ro_pending_state = 0
gpgpu_ep_l2_feature_tvd = 0
gpgpu_ep_l2_feature_adaptive_policy = 0
```

Omitted options resolve to those values in `cache_config`.  The L2 constructor
fails closed if policy is not static or any future functional bit is enabled.
The normal D512 Legacy/Banked overlays remain payload-service variants; they do
not enable Unified allocation or create bypass traffic.  Campaign manifests
record the source/config hashes from the existing frozen runner.
