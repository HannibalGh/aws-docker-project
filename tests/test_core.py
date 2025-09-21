# test_core.py
# Purpose: check the JSON shape and basic properties of the payload
# returned by build_payload_dict(). We don't assert exact numbers because
# the function generates random data; instead we verify structure and invariants.

from src.core import build_payload_dict

def test_payload_shape_and_dedupe():
    # Call the core function (test should not rely on exact values)
    payload = build_payload_dict()

    # Top-level keys should exist
    assert "data" in payload and "timestamp" in payload

    d = payload["data"]

    # Ensure the expected nested keys are present
    assert "unsorted" in d and "sorted" in d
    assert "raw" in d["sorted"] and "unique" in d["sorted"]

    # --- Invariants we expect regardless of randomness ---

    # 1) "raw" should be a sorted version of "unsorted"
    raw = d["sorted"]["raw"]
    assert raw == sorted(raw)

    # 2) "unique" should contain no duplicates (deduped, order preserved by implementation)
    uniq = d["sorted"]["unique"]
    assert len(uniq) == len(set(uniq))
