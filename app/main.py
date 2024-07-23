import sys
from typing import Never

from app.scanner import Scanner

COMMANDS = {"tokenize"}


def _exit_with_message(message: str) -> Never:
    print(message, file=sys.stderr)
    exit(1)


def _get_input() -> tuple[str, str | None]:
    if len(sys.argv) < 3:
        _exit_with_message("Usage: ./your_program.sh tokenize <filename>")

    command = sys.argv[1] if len(sys.argv) >= 1 else None
    filename = sys.argv[2] if len(sys.argv) >= 2 else None

    if command is None:
        _exit_with_message("Command is required")
    if command not in COMMANDS:
        _exit_with_message(f"Unknown command: {command}")

    return command, filename


def main():
    command, filename = _get_input()

    with open(filename) as file:
        file_contents = file.read()

    scanner = Scanner(file_contents)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
