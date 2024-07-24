import sys
from typing import Never

from app.ast_printer import AstPrinter
from app.logger import Logger
from app.parser import Parser
from app.scanner import Scanner
from app.schema import Command

COMMANDS = {Command.TOKENIZE, Command.PARSE}


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


def _run(logger: Logger, command: Command, text: str) -> None:
    scanner = Scanner(logger, text)
    tokens = scanner.scan_tokens()

    if command == Command.TOKENIZE:
        for token in tokens:
            print(token)
        return

    parser = Parser(logger, tokens)
    expression = parser.parse()

    if command == Command.PARSE:
        ast_printer = AstPrinter()
        ast_printer.print(expression)
        return


def main():
    command, filename = _get_input()

    with open(filename) as file:
        file_contents = file.read()

    logger = Logger()
    _run(logger, command, file_contents)

    if logger.had_error:
        exit(65)


if __name__ == "__main__":
    main()
