import sys
from typing import Never

from app.ast_printer import AstPrinter
from app.interpreter import Interpreter
from app.logger import Logger
from app.parser import Parser
from app.scanner import Scanner
from app.schema import Command

COMMANDS = {Command.TOKENIZE, Command.PARSE, Command.INTERPRET}


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


def _run(logger: Logger, interpreter: Interpreter, command: Command, text: str) -> None:
    scanner = Scanner(logger, text)
    tokens = scanner.scan_tokens()

    if command == Command.TOKENIZE:
        for token in tokens:
            print(token)
        return

    if logger.had_error:
        return

    parser = Parser(logger, tokens)

    if command == Command.PARSE:
        expression = parser.parse_expression()
        ast_printer = AstPrinter()
        if expression is not None:
            ast_printer.print(expression)
        return

    statements = parser.parse()

    if logger.had_error:
        return

    interpreter.interpret(statements)


def _run_file(command: Command, filename: str) -> None:
    with open(filename) as file:
        file_contents = file.read()

    logger = Logger()
    interpreter = Interpreter(logger)
    _run(logger, interpreter, command, file_contents)

    if logger.had_error:
        exit(65)
    if logger.had_runtime_error:
        exit(70)


def _run_prompt(command: Command) -> None:
    logger = Logger()
    interpreter = Interpreter(logger)

    while True:
        text = input("> ")
        if not text:
            continue

        _run(logger, interpreter, command, text)

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


"""
program        → declaration* EOF ;

declaration    → varDecl
               | statement ;

statement      → exprStmt
               | printStmt ;

varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;

primary        → "true" | "false" | "nil"
               | NUMBER | STRING
               | "(" expression ")"
               | IDENTIFIER ;
"""
