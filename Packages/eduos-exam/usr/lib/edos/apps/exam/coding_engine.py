import subprocess
import tempfile
import os

class CodingEngine:
    def __init__(self):
        self.language = "python3"

    def set_language(self, lang):
        self.language = lang

    def run_code(self, code, test_input=""):
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
                f.write(code)
                fpath = f.name
            result = subprocess.run(
                [self.language, fpath],
                input=test_input, capture_output=True, text=True, timeout=30
            )
            os.unlink(fpath)
            return {"output": result.stdout, "error": result.stderr,
                    "return_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Time limit exceeded", "return_code": -1}
        except Exception as e:
            return {"output": "", "error": str(e), "return_code": -1}

    def check_test_cases(self, code, test_cases):
        results = []
        for tc in test_cases:
            result = self.run_code(code, tc.get("input", ""))
            expected = tc.get("output", "").strip()
            actual = result["output"].strip()
            results.append({
                "passed": actual == expected,
                "expected": expected,
                "actual": actual,
                "error": result["error"]
            })
        return results
