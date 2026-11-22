"""Static safety scan for Claude-written scene modules (run before anything is imported or rendered).

Generated code may only import an allow-list of packages, may not call eval/exec/open/__import__/compile,
may not touch os/subprocess/sockets/environment variables or secrets, and may not reference narration
modules (shorts.tts, src.explainer.audio_engine, ...). Syntax errors also fail the scan.
"""
from __future__ import annotations

import ast
from pathlib import Path

ALLOWED_IMPORTS = {"manim", "numpy", "math", "random", "dataclasses", "typing", "colorsys", "itertools",
                   "functools", "PIL", "cv2", "moviepy", "generated_animations", "__future__"}
FORBIDDEN_CALLS = {"eval", "exec", "open", "__import__", "compile", "input", "breakpoint", "getattr", "setattr",
                   "globals", "locals", "vars", "delattr"}
FORBIDDEN_NAMES = {"os", "subprocess", "socket", "shutil", "sys", "environ", "getenv", "system", "popen",
                   "__builtins__", "__class__", "__subclasses__", "__globals__"}
FORBIDDEN_TEXT = ("secret", "api_key", "apikey", "token", "password", "shorts.tts", "audio_engine",
                  "narration_module", ".env", "id_rsa")


def scan_source(source: str, filename: str = "<scene>") -> list[str]:
    problems: list[str] = []
    try:
        tree = ast.parse(source, filename)
    except SyntaxError as exc:
        return [f"{filename}: syntax error line {exc.lineno}: {exc.msg}"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    problems.append(f"{filename}:{node.lineno}: import '{a.name}' is not allowed")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level == 0 and root not in ALLOWED_IMPORTS:
                problems.append(f"{filename}:{node.lineno}: import from '{node.module}' is not allowed")
            if node.level == 0 and "tts" in (node.module or ""):
                problems.append(f"{filename}:{node.lineno}: narration modules may not be used by scene code")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            problems.append(f"{filename}:{node.lineno}: call to '{node.func.id}' is not allowed")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            problems.append(f"{filename}:{node.lineno}: name '{node.id}' is not allowed")
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
            problems.append(f"{filename}:{node.lineno}: attribute '.{node.attr}' is not allowed")
    lowered = source.lower()
    for bad in FORBIDDEN_TEXT:
        if bad in lowered:
            problems.append(f"{filename}: forbidden text '{bad}'")
    return problems


def scan_dir(directory: Path) -> list[str]:
    problems: list[str] = []
    for f in sorted(Path(directory).glob("scene_*.py")):
        problems += scan_source(f.read_text(encoding="utf-8"), f.name)
    return problems
