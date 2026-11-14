"""A small interpreter for the currently finalized Box syntax."""
from __future__ import annotations

import re
from typing import Any


class BoxError(Exception):
    """An error raised while parsing or executing a Box program."""


class Interpreter:
    def __init__(self, output=print):
        self.variables: dict[str, Any] = {}
        self.output = output

    @staticmethod
    def _braced(text: str, pattern: str, line_no: int):
        match = re.fullmatch(pattern, text.strip())
        if not match:
            raise BoxError(f"Line {line_no}: invalid syntax")
        return match.groups()

    def run(self, source: str):
        lines = source.splitlines()
        meaningful = [(i + 1, line.strip()) for i, line in enumerate(lines)
                      if line.strip() and not line.strip().startswith("//")]

        if not meaningful or meaningful[0][1] != "#Start#":
            raise BoxError("Err start not found")
        if sum(1 for _, line in meaningful if line == "#Start#") > 1:
            raise BoxError("Error start")
        if meaningful[-1][1] != "#End#":
            raise BoxError("end not found")
        if sum(1 for _, line in meaningful if line == "#End#") > 1:
            raise BoxError("Error end")

        body = meaningful[1:-1]
        i = 0
        while i < len(body):
            line_no, line = body[i]

            # One-line equality condition:
            # yesli box {A}==box {B} to P {Equal}!
            cond = re.fullmatch(
                r"yesli\s+box\s*\{([^{}]+)\}\s*==\s*box\s*\{([^{}]+)\}\s+to\s+P\s*\{(.*)\}!",
                line
            )
            if cond:
                left_name, right_name, message = cond.groups()
                equal = self._get(left_name.strip(), line_no) == self._get(right_name.strip(), line_no)
                if equal:
                    self.output(message)
                if i + 1 < len(body):
                    next_no, next_line = body[i + 1]
                    alt = re.fullmatch(r"Nosli\s+P\s*\{(.*)\}!", next_line)
                    if alt:
                        if not equal:
                            self.output(alt.group(1))
                        i += 1
                i += 1
                continue

            # Variable creation: C box {A}!
            create = re.fullmatch(r"C\s+box\s*\{([^{}]+)\}!", line)
            if create:
                name = create.group(1).strip()
                self._check_name(name, line_no)
                if name in self.variables:
                    raise BoxError(f"Line {line_no}: variable already exists: {name}")
                self.variables[name] = None
                i += 1
                continue

            # Store value: P {123} box {A}!
            store = re.fullmatch(r"P\s*\{(.*)\}\s+box\s*\{([^{}]+)\}!", line)
            if store:
                value, name = store.groups()
                name = name.strip()
                self._check_name(name, line_no)
                self.variables[name] = self._value(value, line_no)
                i += 1
                continue

            # Print variable: >{A}
            show_var = re.fullmatch(r">\s*\{([^{}]+)\}", line)
            if show_var:
                self.output(self._get(show_var.group(1).strip(), line_no))
                i += 1
                continue

            # Print literal: P {Hello}!
            show = re.fullmatch(r"P\s*\{(.*)\}!", line)
            if show:
                self.output(show.group(1))
                i += 1
                continue

            raise BoxError(f"Line {line_no}: unsupported or invalid Box command: {line!r}")

        return self.variables

    def _get(self, name: str, line_no: int):
        if name not in self.variables:
            raise BoxError(f"Line {line_no}: unknown variable: {name}")
        return self.variables[name]

    @staticmethod
    def _check_name(name: str, line_no: int):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            raise BoxError(f"Line {line_no}: invalid variable name: {name}")

    @staticmethod
    def _value(value: str, line_no: int):
        value = value.strip()
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        if re.fullmatch(r"-?\d+\.\d+", value):
            return float(value)
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        if value.startswith('"') and value.endswith('"') and len(value) >= 2:
            return value[1:-1]
        return value
