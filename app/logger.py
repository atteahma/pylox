import sys

from app.errors import InterpreterError


class Logger:
    had_error: bool

    def __init__(self) -> None:
        self.had_error = False
        self.had_runtime_error = False

    def report(self, line: int, where: str, message: str) -> None:
        self.had_error = True

        log_str = f"[line {line}] Error{where}: {message}"
        print(log_str, file=sys.stderr)

    def report_runtime(self, error: InterpreterError) -> None:
        log_str = f"{error.message}\n[line {error.token.line}])"
        print(log_str, file=sys.stderr)

    def reset(self) -> None:
        self.had_error = False
