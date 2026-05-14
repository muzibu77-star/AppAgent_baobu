"""Compatibility stub for Florence-2 dynamic import checks.

Transformers scans remote model files for imports before executing guarded
branches. Florence-2 imports flash_attn only when the real package is available,
but the static check still requires an importable top-level module.
"""
