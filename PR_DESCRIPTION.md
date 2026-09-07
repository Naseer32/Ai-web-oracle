# PR: Enforce strict verdict boolean and confidence normalization

This PR adds a small deterministic helper normalize_result(result) that:
- Ensures `verdict` is a JSON boolean (True/False). Accepts booleans, 1/0, numeric 1.0/0.0, and common strings ("true","false","yes","no","1","0"). Any unrecognized verdict falls back to `False`.
- Ensures `confidence` is exactly one of "high"|"medium"|"low". Accepts those strings case-insensitively, or maps numeric scores: >=0.75 -> high, >=0.40 -> medium, else low. Missing/invalid -> "low".

Why: previously code used bool(result["verdict"]) which treats non-empty strings (including "false") as True; that allows validators to derive one value while the stored contract may hold the opposite. This helper defines a deterministic canonicalization and includes tests.

Files added:
- normalize_result.py
- tests/test_normalize_result.py

Integration notes:
- Replace bool(result["verdict"]) with normalize_result(result)["verdict"]
- Serialize normalized dict before storing so JSON booleans are preserved (json.dumps(normalized))
