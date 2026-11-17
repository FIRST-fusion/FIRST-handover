#!/usr/bin/env python3
"""CLI tests for the numerical regression comparator.

All fixtures are synthetic. Each case runs in a temporary directory and
checks that the expected reference bytes and mtime stay unchanged.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "compare.py"


def _reject_constant(constant: str) -> None:
    raise ValueError(constant)


def _dump(document: object) -> str:
    return json.dumps(document)


class CompareCliTests(unittest.TestCase):
    def run_compare(self, actual_text: str, expected_text: str) -> tuple[int, dict]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual_path = root / "actual.json"
            expected_path = root / "expected.json"
            actual_path.write_text(actual_text, encoding="utf-8")
            expected_path.write_text(expected_text, encoding="utf-8")
            before = expected_path.read_bytes()
            before_stat = expected_path.stat()
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), str(actual_path), str(expected_path)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            after = expected_path.read_bytes()
            after_stat = expected_path.stat()
        self.assertEqual(before, after)
        self.assertEqual(before_stat.st_mtime_ns, after_stat.st_mtime_ns)
        self.assertEqual(before_stat.st_ino, after_stat.st_ino)
        self.assertEqual(proc.stderr, "")
        self.assertTrue(proc.stdout.endswith("\n"))
        report = json.loads(proc.stdout, parse_constant=_reject_constant)
        self.assertIs(report["passed"], proc.returncode == 0)
        self.assertIsInstance(report["errors"], list)
        return proc.returncode, report

    def test_exact_pass(self) -> None:
        actual = {
            "metrics": {"beta": 0.1, "gamma": 9},
            "labels": {"dcon.fixed": "unstable", "note": "extra"},
            "valid": True,
            "run": "synthetic",
        }
        expected = {
            "metrics": {"beta": {"value": 0.1, "rtol": 0, "atol": 0, "unit": "1"}},
            "labels": {"dcon.fixed": "unstable"},
            "source": "synthetic-reference",
        }
        code, report = self.run_compare(_dump(actual), _dump(expected))
        self.assertEqual(code, 0)
        self.assertEqual(report, {"passed": True, "errors": []})

    def test_tolerance_pass_and_fail(self) -> None:
        expected = {
            "metrics": {
                "beta": {"value": 10, "rtol": 0, "atol": 1},
                "q": {"value": -20, "rtol": 1, "atol": 0},
            },
            "labels": {"dcon.fixed": "unstable"},
        }
        passing = {
            "metrics": {"beta": 11, "q": -40},
            "labels": {"dcon.fixed": "unstable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(passing), _dump(expected))
        self.assertEqual(code, 0)
        self.assertEqual(report["errors"], [])

        failing = {
            "metrics": {"beta": 12, "q": -40},
            "labels": {"dcon.fixed": "unstable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(failing), _dump(expected))
        self.assertEqual(code, 1)
        self.assertEqual(len(report["errors"]), 1)
        self.assertEqual(report["errors"][0]["code"], "metric")
        self.assertEqual(report["errors"][0]["key"], "beta")
        self.assertEqual(report["errors"][0]["abs_diff"], 2)
        self.assertEqual(report["errors"][0]["limit"], 1)

    def test_missing_metrics(self) -> None:
        expected = _dump(
            {
                "metrics": {"beta": {"value": 0.1, "rtol": 1e-6, "atol": 1e-10}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        omitted_key = {
            "metrics": {},
            "labels": {"dcon.fixed": "unstable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(omitted_key), expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "missing_metric")
        self.assertEqual(report["errors"][0]["key"], "beta")

        omitted_object = {
            "labels": {"dcon.fixed": "unstable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(omitted_object), expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "missing_metric")
        self.assertNotIn("key", report["errors"][0])

    def test_nan_rejected(self) -> None:
        expected = _dump(
            {
                "metrics": {"beta": {"value": 0.1, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        actual = '{"metrics": {"beta": NaN}, "labels": {"dcon.fixed": "unstable"}, "valid": true}'
        code, report = self.run_compare(actual, expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "nonfinite")
        self.assertEqual(report["errors"][0]["key"], "beta")
        self.assertNotIn("NaN", json.dumps(report))

        expected_nan = (
            '{"metrics": {"beta": {"value": NaN, "rtol": 0, "atol": 0}}, '
            '"labels": {"dcon.fixed": "unstable"}}'
        )
        actual_ok = '{"metrics": {"beta": 0.1}, "labels": {"dcon.fixed": "unstable"}, "valid": true}'
        code, report = self.run_compare(actual_ok, expected_nan)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "nonfinite")

    def test_false_valid(self) -> None:
        expected = _dump(
            {
                "metrics": {"beta": {"value": 1, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        cases = (
            {"metrics": {"beta": 1}, "labels": {"dcon.fixed": "unstable"}, "valid": False},
            {"metrics": {"beta": 1}, "labels": {"dcon.fixed": "unstable"}, "valid": 1},
            {"metrics": {"beta": 1}, "labels": {"dcon.fixed": "unstable"}, "valid": "true"},
            {"metrics": {"beta": 1}, "labels": {"dcon.fixed": "unstable"}},
        )
        for actual in cases:
            with self.subTest(valid=actual.get("valid", "missing")):
                code, report = self.run_compare(_dump(actual), expected)
                self.assertEqual(code, 1)
                self.assertFalse(report["passed"])
                self.assertEqual([item["code"] for item in report["errors"]], ["valid"])

    def test_label_mismatch_and_missing_label(self) -> None:
        expected = _dump(
            {
                "metrics": {"beta": {"value": 1, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        mismatch = {
            "metrics": {"beta": 1},
            "labels": {"dcon.fixed": "stable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(mismatch), expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "label")
        self.assertEqual(report["errors"][0]["key"], "dcon.fixed")

        missing = {"metrics": {"beta": 1}, "labels": {}, "valid": True}
        code, report = self.run_compare(_dump(missing), expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "missing_label")
        self.assertEqual(report["errors"][0]["key"], "dcon.fixed")

    def test_dotted_keys_are_literal(self) -> None:
        expected = _dump(
            {
                "metrics": {"core.beta": {"value": 0.25, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        nested = {
            "metrics": {"core": {"beta": 0.25}},
            "labels": {"dcon": {"fixed": "unstable"}},
            "valid": True,
        }
        code, report = self.run_compare(_dump(nested), expected)
        self.assertEqual(code, 1)
        self.assertEqual(
            [(item["code"], item.get("key")) for item in report["errors"]],
            [("missing_metric", "core.beta"), ("missing_label", "dcon.fixed")],
        )

        literal = {
            "metrics": {"core.beta": 0.25},
            "labels": {"dcon.fixed": "unstable"},
            "valid": True,
        }
        code, report = self.run_compare(_dump(literal), expected)
        self.assertEqual(code, 0)
        self.assertTrue(report["passed"])

    def test_malformed_json_and_schema(self) -> None:
        valid_actual = '{"metrics": {"beta": 1}, "labels": {"dcon.fixed": "unstable"}, "valid": true}'
        valid_expected = _dump(
            {
                "metrics": {"beta": {"value": 1, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare("{", valid_expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "json")

        code, report = self.run_compare(valid_actual, "[")
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "json")

        for actual in ("[]", "null", _dump({"metrics": [], "labels": {}, "valid": True})):
            with self.subTest(actual=actual):
                code, report = self.run_compare(actual, valid_expected)
                self.assertEqual(code, 1)
                self.assertEqual(report["errors"][0]["code"], "schema")

        incomplete = _dump(
            {
                "metrics": {"beta": {"value": 1}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare(valid_actual, incomplete)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "schema")
        self.assertEqual(report["errors"][0]["key"], "beta")

        empty_spec = _dump(
            {
                "metrics": {"beta": {}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare(valid_actual, empty_spec)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "empty_metric_spec")
        self.assertEqual(report["errors"][0]["key"], "beta")

    def test_malformed_tolerance(self) -> None:
        actual = '{"metrics": {"beta": 999}, "labels": {"dcon.fixed": "unstable"}, "valid": true}'
        negative = _dump(
            {
                "metrics": {"beta": {"value": 0.1, "rtol": -1e-6, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare(actual, negative)
        self.assertEqual(code, 1)
        self.assertEqual([item["code"] for item in report["errors"]], ["tolerance"])

        nonfinite = (
            '{"metrics": {"beta": {"value": 0.1, "rtol": Infinity, "atol": -1}}, '
            '"labels": {"dcon.fixed": "unstable"}}'
        )
        code, report = self.run_compare(actual, nonfinite)
        self.assertEqual(code, 1)
        self.assertEqual([item["code"] for item in report["errors"]], ["tolerance", "tolerance"])
        self.assertNotIn("Infinity", json.dumps(report))

        boolean = _dump(
            {
                "metrics": {"beta": {"value": True, "rtol": True, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare(actual, boolean)
        self.assertEqual(code, 1)
        self.assertEqual(
            [item["code"] for item in report["errors"]],
            ["not_numeric", "tolerance"],
        )

    def test_boolean_actual_is_not_numeric(self) -> None:
        actual = _dump(
            {
                "metrics": {"beta": True},
                "labels": {"dcon.fixed": "unstable"},
                "valid": True,
            }
        )
        expected = _dump(
            {
                "metrics": {"beta": {"value": 1, "rtol": 0, "atol": 0}},
                "labels": {"dcon.fixed": "unstable"},
            }
        )
        code, report = self.run_compare(actual, expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "not_numeric")
        self.assertEqual(report["errors"][0]["key"], "beta")

    def test_reference_not_mutated(self) -> None:
        expected = (
            '{\n'
            '"metrics" : {"beta": {"value": 1, "rtol": 0, "atol": 0}} ,\n'
            '"labels" : {"dcon.fixed": "unstable"}\n'
            '}\n'
        )
        actual = '{"metrics": {"beta": 2}, "labels": {"dcon.fixed": "unstable"}, "valid": true}'
        code, report = self.run_compare(actual, expected)
        self.assertEqual(code, 1)
        self.assertEqual(report["errors"][0]["code"], "metric")
        self.assertIn('"metrics" :', expected)

    def test_usage(self) -> None:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, "")
        report = json.loads(proc.stdout, parse_constant=_reject_constant)
        self.assertFalse(report["passed"])
        self.assertEqual(report["errors"][0]["code"], "usage")


if __name__ == "__main__":
    unittest.main()
