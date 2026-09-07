"""
normalize_result.normalize_result(result: dict) -> dict
Deterministically normalizes and validates model output so:
 - 'verdict' is returned as a JSON boolean (True/False)
 - 'confidence' is returned as one of: "high", "medium", "low"

Policy (deterministic):
 - If verdict is a JSON boolean, keep it.
 - If verdict is a string, accept "true"/"false" (case-insensitive), also accept "1"/"0", "yes"/"no".
 - If verdict is a numeric 1/0, map 1->True, 0->False.
 - Any other/unrecognized verdict -> canonical False.
 - If confidence is the string "high"/"medium"/"low" (case-insensitive) keep it.
 - If confidence is numeric (0.0-1.0): >=0.75 -> "high", >=0.40 -> "medium", else "low".
 - Missing/invalid confidence -> "low".
 - The function returns {'verdict': bool, 'confidence': 'high'|'medium'|'low'} only.
"""

from typing import Any, Dict, Optional


def _parse_bool_candidate(val: Any) -> Optional[bool]:
    if isinstance(val, bool):
        return val
    if isinstance(val, int):
        if val == 1:
            return True
        if val == 0:
            return False
        return None
    if isinstance(val, float):
        # only accept exact 1.0 and 0.0 as booleans
        if val == 1.0:
            return True
        if val == 0.0:
            return False
        return None
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"true", "t", "yes", "y", "1"}:
            return True
        if s in {"false", "f", "no", "n", "0"}:
            return False
        return None
    return None


def _parse_confidence_candidate(val: Any) -> Optional[str]:
    if isinstance(val, str):
        s = val.strip().lower()
        if s in {"high", "medium", "low"}:
            return s
        # if string looks numeric, try numeric mapping
        try:
            f = float(s)
        except Exception:
            return None
    elif isinstance(val, (int, float)):
        f = float(val)
    else:
        return None

    # numeric mapping (0.0-1.0 expected but accepts any numeric)
    if f >= 0.75:
        return "high"
    if f >= 0.40:
        return "medium"
    return "low"


def normalize_result(result: Dict[str, Any]) -> Dict[str, object]:
    """
    Normalize a model/agent result to a strict schema:
      { "verdict": bool, "confidence": "high"|"medium"|"low" }

    Deterministic fallback:
      - Unparseable/absent verdict => False
      - Unparseable/absent confidence => "low"

    Use this in both leader/validator code paths and immediately before storing
    the result (database, contract, etc.) to ensure everyone agrees.
    """
    # Defensive: ensure we accept dict-like input
    if not isinstance(result, dict):
        # Not a dict at all — deterministic fallback
        return {"verdict": False, "confidence": "low"}

    # Verdict
    raw_verdict = result.get("verdict", None)
    parsed_verdict = _parse_bool_candidate(raw_verdict)
    if parsed_verdict is None:
        # deterministic fallback: False (conservative)
        parsed_verdict = False

    # Confidence
    raw_conf = result.get("confidence", None)
    parsed_conf = _parse_confidence_candidate(raw_conf)
    if parsed_conf is None:
        # deterministic fallback: "low"
        parsed_conf = "low"

    # Return canonical dict with strict types
    return {"verdict": bool(parsed_verdict), "confidence": parsed_conf}
