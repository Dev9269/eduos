"""Tests for EduOS Coding Engine"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "coding_engine",
    "Packages/eduos-exam/usr/lib/edos/apps/exam/coding_engine.py"
)
coding_engine_mod = spec.loader.load_module()
CodingEngine = coding_engine_mod.CodingEngine

# Dev-machine shim: on Windows the `python3` launcher may be a store stub.
# If the configured interpreter is unusable, fall back to the running one.
# On FreeBSD/Linux CI this block no-ops.
if not coding_engine_mod.LANGUAGE_CONFIG["python3"]["available"] or sys.platform == "win32":
    try:
        import subprocess
        probe = subprocess.run(
            ["python3", "-c", "print(1)"], capture_output=True, timeout=10
        )
        usable = probe.returncode == 0
    except Exception:
        usable = False
    if not usable:
        coding_engine_mod.LANGUAGE_CONFIG["python3"]["available"] = True
        coding_engine_mod.LANGUAGE_CONFIG["python3"]["run"] = [sys.executable, "{file}"]


def test_python_hello_world():
    engine = CodingEngine()
    result = engine.run_code('print("hello world")')
    assert result["output"].strip() == "hello world"
    assert result["return_code"] == 0

def test_python_with_input():
    engine = CodingEngine()
    result = engine.run_code('x = int(input()); print(x * 2)', test_input="5")
    assert result["output"].strip() == "10"

def test_python_infinite_loop_timeout():
    engine = CodingEngine()
    result = engine.run_code('while True: pass', timeout=2)
    assert result["timed_out"] is True

def test_python_syntax_error():
    engine = CodingEngine()
    result = engine.run_code('def broken(:\n    pass')
    assert result["return_code"] != 0
    assert result["error"] != ""

def test_available_languages():
    engine = CodingEngine()
    langs = engine.available_languages()
    assert "python3" in langs  # always available in test env

def test_unsupported_language():
    engine = CodingEngine()
    try:
        engine.set_language("cobol")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_test_cases_pass():
    engine = CodingEngine()
    results = engine.check_test_cases(
        'a, b = map(int, input().split()); print(a + b)',
        [{"input": "1 2", "output": "3"},
         {"input": "10 20", "output": "30"}]
    )
    assert all(r["passed"] for r in results)

def test_test_cases_fail():
    engine = CodingEngine()
    results = engine.check_test_cases(
        'print("wrong")',
        [{"input": "", "output": "right"}]
    )
    assert not results[0]["passed"]

def test_output_size_limit():
    engine = CodingEngine()
    result = engine.run_code('print("A" * 100000)')
    assert len(result["output"]) <= coding_engine_mod.MAX_OUTPUT_BYTES + 200
