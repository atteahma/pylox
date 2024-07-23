import sys

COMMANDS = {"tokenize"}


def _get_input():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in COMMANDS:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    return command, filename


def main():
    command, filename = _get_input()

    with open(filename) as file:
        file_contents = file.read()

    if file_contents:
        raise NotImplementedError("Scanner not implemented")
    else:
        print("EOF  null")


if __name__ == "__main__":
    main()
