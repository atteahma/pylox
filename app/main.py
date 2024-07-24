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
    if len(sys.argv) not in (2, 3):
        _exit_with_message(
            "Usage: ./your_program.sh <command> <filename> or ./your_program.sh <command>"
        )

    command = sys.argv[1] if len(sys.argv) >= 2 else None
    filename = sys.argv[2] if len(sys.argv) >= 3 else None

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

    if logger.had_error:
        return

    parser = Parser(logger, tokens)
    expression = parser.parse()

    if logger.had_error:
        return

    # this should hold if logger.had_error = False
    assert expression is not None

    if command == Command.PARSE:
        ast_printer = AstPrinter()
        ast_printer.print(expression)
        return


def _run_file(command: Command, filename: str) -> None:
    with open(filename) as file:
        file_contents = file.read()

    logger = Logger()
    _run(logger, command, file_contents)

    if logger.had_error:
        exit(65)


def _run_prompt(command: Command) -> None:
    logger = Logger()

    while True:
        text = input("> ")
        if not text:
            break

        _run(logger, command, text)

        logger.reset()


def main():
    command, filename = _get_input()

    if filename is None:
        _run_prompt(command)
    else:
        _run_file(command, filename)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Got interrupt, exiting...")
