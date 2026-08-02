"""
EduOS Coding Engine — Secure multi-language code execution
Supports: Python, Java, C, C++, JavaScript (Node)
Security: process limits, memory cap, output cap, timeout
"""

import subprocess
import tempfile
import os
import shutil
import platform
from pathlib import Path

try:
    import resource
except ImportError:  # Windows — limits are enforced via timeout only
    resource = None

# Per-language config: (file_extension, compile_command, run_command)
LANGUAGE_CONFIG = {
    "python3": {
        "ext": ".py",
        "compile": None,  # interpreted
        "run": ["python3", "{file}"],
        "available": shutil.which("python3") is not None,
    },
    "java": {
        "ext": ".java",
        "compile": ["javac", "{file}"],
        "run": ["java", "-cp", "{dir}", "{classname}"],
        "available": shutil.which("javac") is not None,
    },
    "c": {
        "ext": ".c",
        "compile": ["gcc", "-O2", "-o", "{out}", "{file}", "-lm"],
        "run": ["{out}"],
        "available": shutil.which("gcc") is not None,
    },
    "cpp": {
        "ext": ".cpp",
        "compile": ["g++", "-O2", "-o", "{out}", "{file}"],
        "run": ["{out}"],
        "available": shutil.which("g++") is not None,
    },
    "javascript": {
        "ext": ".js",
        "compile": None,
        "run": ["node", "{file}"],
        "available": shutil.which("node") is not None,
    },
}

MAX_OUTPUT_BYTES = 64 * 1024       # 64 KB output limit
MAX_MEMORY_MB = 256                 # 256 MB memory limit
DEFAULT_TIMEOUT = 10                # seconds


class CodingEngine:
    def __init__(self):
        self.language = "python3"

    def set_language(self, lang: str):
        lang = lang.lower().strip()
        if lang not in LANGUAGE_CONFIG:
            raise ValueError(f"Unsupported language: {lang}. Supported: {list(LANGUAGE_CONFIG.keys())}")
        if not LANGUAGE_CONFIG[lang]["available"]:
            raise RuntimeError(f"{lang} is not installed on this system")
        self.language = lang

    def available_languages(self) -> list:
        return [lang for lang, cfg in LANGUAGE_CONFIG.items() if cfg["available"]]

    def _set_limits(self):
        """Set process resource limits (Unix only)"""
        if platform.system() in ("Linux", "FreeBSD", "Darwin"):
            try:
                mem_bytes = MAX_MEMORY_MB * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
                resource.setrlimit(resource.RLIMIT_CPU, (DEFAULT_TIMEOUT, DEFAULT_TIMEOUT))
                # Prevent fork bombs
                resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))
            except Exception:
                pass  # Best-effort

    def run_code(self, code: str, test_input: str = "",
                 timeout: int = DEFAULT_TIMEOUT) -> dict:
        cfg = LANGUAGE_CONFIG.get(self.language)
        if not cfg:
            return {"output": "", "error": f"Unknown language: {self.language}",
                    "return_code": -1, "timed_out": False}

        with tempfile.TemporaryDirectory(prefix="eduos_exec_") as tmpdir:
            ext = cfg["ext"]

            # Java: filename must match class name
            if self.language == "java":
                classname = "Solution"
                fname = f"{classname}{ext}"
                # Wrap in class if student didn't
                if "class " not in code:
                    code = f"public class Solution {{\n    public static void main(String[] args) {{\n{code}\n    }}\n}}"
            else:
                fname = f"code{ext}"
                classname = None

            fpath = os.path.join(tmpdir, fname)
            outpath = os.path.join(tmpdir, "out")

            with open(fpath, "w") as f:
                f.write(code)

            # Compile if needed
            if cfg["compile"]:
                compile_cmd = [
                    part.replace("{file}", fpath)
                         .replace("{out}", outpath)
                         .replace("{dir}", tmpdir)
                         .replace("{classname}", classname or "Solution")
                    for part in cfg["compile"]
                ]
                try:
                    compile_result = subprocess.run(
                        compile_cmd,
                        capture_output=True, text=True, timeout=30,
                        cwd=tmpdir
                    )
                    if compile_result.returncode != 0:
                        return {
                            "output": "",
                            "error": f"Compilation failed:\n{compile_result.stderr[:2000]}",
                            "return_code": compile_result.returncode,
                            "timed_out": False
                        }
                except subprocess.TimeoutExpired:
                    return {"output": "", "error": "Compilation timed out",
                            "return_code": -1, "timed_out": False}

            # Build run command
            run_cmd = [
                part.replace("{file}", fpath)
                     .replace("{out}", outpath)
                     .replace("{dir}", tmpdir)
                     .replace("{classname}", classname or "")
                for part in cfg["run"]
            ]

            try:
                proc = subprocess.Popen(
                    run_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir,
                    preexec_fn=self._set_limits if platform.system() != "Windows" else None,
                )
                try:
                    stdout, stderr = proc.communicate(
                        input=test_input.encode() if test_input else b"",
                        timeout=timeout
                    )
                    # Enforce output size limit
                    output = stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
                    error = stderr[:4096].decode("utf-8", errors="replace")
                    if len(stdout) > MAX_OUTPUT_BYTES:
                        output += f"\n[Output truncated — exceeded {MAX_OUTPUT_BYTES} bytes]"
                    return {
                        "output": output,
                        "error": error,
                        "return_code": proc.returncode,
                        "timed_out": False
                    }
                except subprocess.TimeoutExpired:
                    proc.kill()
                    try:
                        # Reap process + close pipes so temp dir can be removed
                        proc.communicate(timeout=5)
                    except Exception:
                        pass
                    return {"output": "", "error": f"Time limit exceeded ({timeout}s)",
                            "return_code": -1, "timed_out": True}
            except Exception as e:
                return {"output": "", "error": str(e), "return_code": -1, "timed_out": False}

    def check_test_cases(self, code: str, test_cases: list) -> list:
        """Run code against multiple test cases"""
        results = []
        for i, tc in enumerate(test_cases):
            result = self.run_code(code, tc.get("input", ""))
            expected = tc.get("output", "").strip()
            actual = result["output"].strip()
            results.append({
                "test_case": i + 1,
                "passed": actual == expected and result["return_code"] == 0,
                "expected": expected,
                "actual": actual,
                "error": result["error"],
                "timed_out": result.get("timed_out", False),
            })
        return results
