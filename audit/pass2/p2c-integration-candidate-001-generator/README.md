# P2-C integration candidate generator

`generator.py.gz.b64` is the deterministic, compressed generator used only by the disposable P2-C proof workflow.

Expected decoded Python SHA-256:

`ed55dadfbcff934b3d63d179b26d6a60bd91bf83cf1a3b16952ebf05c2b980cc`

The generator produces an inactive candidate with 79 production actors, 8 explicit privileged owner brokers, 87 exact-source policy actors, and five per-realm insertion sequences. It does not edit production runtime files.

`part00.b64` is an incomplete staging fragment and is intentionally ignored by the corrected proof workflow.
