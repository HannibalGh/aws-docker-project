import random
from datetime import datetime, timezone


def _dedupe_sorted(values):
    """Return unique values from a sorted list (single pass)."""
    unique = []
    last = None
    for v in values:
        if v != last:
            unique.append(v)
            last = v
    return unique


def build_payload_dict():
    """Generate random numbers and return unsorted, sorted, unique + timestamp."""
    unsorted_list = [random.randint(1, 30) for _ in range(15)]
    raw_sorted = sorted(unsorted_list)
    unique = _dedupe_sorted(raw_sorted)

    return {
        "data": {
            "unsorted": unsorted_list,
            "sorted": {
                "raw": raw_sorted,
                "unique": unique
            }
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }
