# PyLox

This is a pure Python from scratch implementation of a tree-walking interpreter for the Lox language, following the book at https://craftinginterpreters.com. It implements all of the core features, some challenges, and some completely extra features.

To see some things the interpreter supports, see [test.lox](https://github.com/atteahma/pylox/blob/a08f9daa66831e7c5e4ce35746829671fdd4b18c/test.lox).

## Features

Core Features:
- Tokens and Lexing
- Abstract Syntax Trees
- Recursive Descent Parsing
- Prefix and Infix Expressions
- Runtime representation of Objects
- Interpreting code using the Visitor Pattern
- Lexical Scope
- Environment Chains for Storing Variables
- Control Flow
- Functions With Parameters
- Closures
- Static Variable Resolution and Error Detection
- Classes
- Constructors
- Fields
- Methods
- Inheritance

Challenges:
- Ternary expressions (partial)
- Break statements

Extra Features:
- Random builtin
- RandInt builtin
- Stringify builtin

## Getting Started

### Prerequisites

- Python 3.11
- Pipenv

### Running

To run in REPL mode:
```
$ ./run.sh interpret
```

To run on a file:
```
$ ./run.sh interpret <filename>
```

### Running the tests

`$ pytest`
