from normalize_result import normalize_result


def test_bool_inputs():
    assert normalize_result({"verdict": True, "confidence": "high"}) == {"verdict": True, "confidence": "high"}
    assert normalize_result({"verdict": False, "confidence": "low"}) == {"verdict": False, "confidence": "low"}


def test_string_boolean_inputs():
    assert normalize_result({"verdict": "true", "confidence": "HIGH"}) == {"verdict": True, "confidence": "high"}
    assert normalize_result({"verdict": "False", "confidence": "MeDium"}) == {"verdict": False, "confidence": "medium"}


def test_numeric_inputs():
    assert normalize_result({"verdict": 1, "confidence": 0.9}) == {"verdict": True, "confidence": "high"}
    assert normalize_result({"verdict": 0, "confidence": 0.5}) == {"verdict": False, "confidence": "medium"}
    assert normalize_result({"verdict": 0.0, "confidence": 0.2}) == {"verdict": False, "confidence": "low"}


def test_malformed_inputs():
    # string "false" must not become True due to bool("false") behavior
    assert normalize_result({"verdict": "false"}) == {"verdict": False, "confidence": "low"}
    # unknown confidence -> low
    assert normalize_result({"verdict": "true", "confidence": "unknown"}) == {"verdict": True, "confidence": "low"}
    # non-dict input
    assert normalize_result(None) == {"verdict": False, "confidence": "low"}
