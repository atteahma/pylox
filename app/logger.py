import sys


class Logger:
    had_error: bool

    def __init__(self) -> None:
        self.had_error = False

    def _log(self, line: int, where: str, message: str) -> None:
        log_str = f"[line {line}] Error{where}: {message}"
        print(log_str, file=sys.stderr)

    def log_error(self, line: int, message: str) -> None:
        self.had_error = True
        self._log(line, "", message)
