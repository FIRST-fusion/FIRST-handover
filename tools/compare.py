#!/usr/bin/env python3
"""Compare actual numerical results with an expected reference.

The expected file is read and never written. Metric and label names are
literal strings, including names that contain dots.
"""

from __future__ import annotations

import json
import math
import sys
from typing import Any

def _isfinite(value: Any) -> bool:
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        return False


USAGE = "usage: python3 tools/compare.py ACTUAL.json EXPECTED.json"
_REQUIRED_SPEC = ("value", "rtol", "atol")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 2:
        return _emit(_fail([_err("usage", USAGE)]))

    actual, actual_error = _load_json(argv[0])
    expected, expected_error = _load_json(argv[1])
    errors = [item for item in (actual_error, expected_error) if item is not None]
    if errors:
        return _emit(_fail(errors))
    return _emit(compare(actual, expected))


def compare(actual: Any, expected: Any) -> dict[str, Any]:
    """Return ``{"passed": bool, "errors": [...]}`` without mutating inputs."""
    errors: list[dict[str, Any]] = []
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        if not isinstance(actual, dict):
            errors.append(_err("schema", "actual document must be a JSON object"))
        if not isinstance(expected, dict):
            errors.append(_err("schema", "expected document must be a JSON object"))
        return _fail(errors)

    if actual.get("valid") is not True:
        errors.append(_err("valid", "actual valid must be exactly true"))

    actual_metrics = _require_mapping(actual, "metrics", "actual", errors)
    actual_labels = _require_mapping(actual, "labels", "actual", errors)
    expected_metrics = _require_mapping(expected, "metrics", "expected", errors)
    expected_labels = _require_mapping(expected, "labels", "expected", errors)

    if isinstance(expected_metrics, dict) and not expected_metrics:
        errors.append(_err("empty_metrics", "reference metrics must not be empty"))

    if isinstance(expected_metrics, dict) and isinstance(actual_metrics, dict):
        _compare_metrics(actual_metrics, expected_metrics, errors)
    if isinstance(expected_labels, dict) and isinstance(actual_labels, dict):
        _compare_labels(actual_labels, expected_labels, errors)

    if errors:
        return _fail(errors)
    return {"passed": True, "errors": []}


def _compare_metrics(
    actual: dict[str, Any],
    expected: dict[str, Any],
    errors: list[dict[str, Any]],
) -> None:
    # Keys are literal. "core.beta" is one name, not a nested lookup.
    for key, spec in expected.items():
        parsed = _parse_metric_spec(key, spec, errors)
        if parsed is None:
            continue
        expected_value, rtol, atol = parsed
        if key not in actual:
            errors.append(_err("missing_metric", "missing metric", key=key))
            continue
        actual_value = actual[key]
        if isinstance(actual_value, bool) or not isinstance(actual_value, (int, float)):
            errors.append(
                _err("not_numeric", "metric value must be a finite number", key=key)
            )
            continue
        if not _isfinite(actual_value):
            errors.append(_err("nonfinite", "metric value must be finite", key=key))
            continue
        diff, limit, ok = _within_tolerance(actual_value, expected_value, rtol, atol)
        if ok:
            continue
        item = _err("metric", "outside tolerance", key=key)
        if diff is not None and limit is not None:
            item["abs_diff"] = diff
            item["limit"] = limit
        errors.append(item)


def _compare_labels(
    actual: dict[str, Any],
    expected: dict[str, Any],
    errors: list[dict[str, Any]],
) -> None:
    for key, expected_value in expected.items():
        if key not in actual:
            errors.append(_err("missing_label", "missing label", key=key))
            continue
        actual_value = actual[key]
        if _contains_nonfinite(actual_value) or _contains_nonfinite(expected_value):
            errors.append(_err("nonfinite", "label value must be finite", key=key))
            continue
        if not _exactly_equal(actual_value, expected_value):
            errors.append(_err("label", "label mismatch", key=key))


def _parse_metric_spec(
    key: str,
    spec: Any,
    errors: list[dict[str, Any]],
) -> tuple[Any, Any, Any] | None:
    if not isinstance(spec, dict):
        errors.append(_err("schema", "metric specification must be a JSON object", key=key))
        return None
    if len(spec) == 0:
        errors.append(_err("empty_metric_spec", "metric specification is empty", key=key))
        return None
    if any(name not in spec for name in _REQUIRED_SPEC):
        errors.append(
            _err(
                "schema",
                "metric specification requires value, rtol, and atol",
                key=key,
            )
        )
        return None

    value = spec["value"]
    rtol = spec["rtol"]
    atol = spec["atol"]
    value_ok = True
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(_err("not_numeric", "expected value must be a finite number", key=key))
        value_ok = False
    elif not _isfinite(value):
        errors.append(_err("nonfinite", "expected value must be finite", key=key))
        value_ok = False
    if not _tolerances_ok(key, rtol, atol, errors) or not value_ok:
        return None
    return value, rtol, atol


def _tolerances_ok(
    key: str,
    rtol: Any,
    atol: Any,
    errors: list[dict[str, Any]],
) -> bool:
    ok = True
    for name, tolerance in (("rtol", rtol), ("atol", atol)):
        if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
            errors.append(
                _err("tolerance", f"{name} must be a finite non-negative number", key=key)
            )
            ok = False
            continue
        if not _isfinite(tolerance) or tolerance < 0:
            errors.append(
                _err("tolerance", f"{name} must be a finite non-negative number", key=key)
            )
            ok = False
    return ok


def _within_tolerance(
    actual: int | float,
    expected: int | float,
    rtol: int | float,
    atol: int | float,
) -> tuple[int | float | None, int | float | None, bool]:
    """Return abs(actual-expected) <= atol + rtol * abs(expected)."""
    try:
        diff = abs(actual - expected)
        limit = atol + rtol * abs(expected)
    except OverflowError:
        return None, None, False
    if (
        isinstance(diff, bool)
        or isinstance(limit, bool)
        or not isinstance(diff, (int, float))
        or not isinstance(limit, (int, float))
        or not _isfinite(diff)
        or not _isfinite(limit)
    ):
        return None, None, False
    return diff, limit, diff <= limit


def _require_mapping(
    document: dict[str, Any],
    name: str,
    side: str,
    errors: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if name not in document:
        code = "missing_metric" if name == "metrics" else "missing_label"
        errors.append(_err(code, f"{side} {name} is missing"))
        return None
    value = document[name]
    if not isinstance(value, dict):
        errors.append(_err("schema", f"{side} {name} must be a JSON object"))
        return None
    return value


def _contains_nonfinite(value: Any) -> bool:
    if isinstance(value, bool) or isinstance(value, int):
        return False
    if isinstance(value, float):
        return not _isfinite(value)
    if isinstance(value, list):
        return any(_contains_nonfinite(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_nonfinite(item) for item in value.values())
    return False


def _exactly_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return _isfinite(left) and _isfinite(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False
        return all(_exactly_equal(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            _exactly_equal(a, b) for a, b in zip(left, right)
        )
    return type(left) is type(right) and left == right


def _load_json(path: str) -> tuple[Any, dict[str, Any] | None]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        detail = exc.strerror or str(exc)
        return None, _err("io", f"cannot read {path}: {detail}")
    except UnicodeError as exc:
        return None, _err("io", f"cannot read {path}: {exc}")
    try:
        return json.loads(text), None
    except json.JSONDecodeError as exc:
        return None, _err("json", f"malformed JSON in {path}: {exc.msg}")


def _err(code: str, message: str, key: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "message": message}
    if key is not None:
        item["key"] = key
    return item


def _fail(errors: list[dict[str, Any]]) -> dict[str, Any]:
    return {"passed": False, "errors": errors}


def _emit(report: dict[str, Any]) -> int:
    print(json.dumps(report, allow_nan=False, separators=(",", ":")))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
