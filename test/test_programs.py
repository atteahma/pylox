from collections.abc import Generator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from functools import cache
import io
from typing import Any
from app import main
from app.schema import Command


def _code(text: str) -> str:
    text = text.strip("\n")
    lines = text.split("\n")
    indent = len(lines[0]) - len(lines[0].lstrip())
    return "\n".join(line[indent:] for line in lines)


def _lines(*lines: Any) -> str:
    if len(lines) == 1 and isinstance(lines[0], Generator):
        lines = tuple(lines[0])
    return "\n".join(map(str, lines))


@contextmanager
def _redirect() -> Generator[tuple[io.StringIO, io.StringIO], None, None]:
    with io.StringIO() as stdout, redirect_stdout(stdout):
        with io.StringIO() as stderr, redirect_stderr(stderr):
            yield stdout, stderr


@cache
def _fib(n: int) -> int:
    if n <= 1:
        return n
    return _fib(n - 2) + _fib(n - 1)


def test_fib():
    code = _code(
        """
        fun fib(n) {
            if (n <= 1) return n;
            return fib(n - 2) + fib(n - 1);
        }

        for (var i = 0; i < 20; i = i + 1) {
            print fib(i);
        }
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == _lines(_fib(i) for i in range(20))
    assert error == ""


def test_closure():
    code = _code(
        """
        fun makeCounter() {
            var i = 0;
            fun count() {
                i = i + 1;
                return i;
            }
            return count;
        }

        var counter = makeCounter();
        print counter();
        print counter();
        print counter();
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == _lines(1, 2, 3)
    assert error == ""


def test_shadowing():
    code = _code(
        """
        var a = "global";
        {
            fun showA() {
                print a;
            }

            showA();
            var a = "block";
            showA();
        }
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == _lines("global", "global")
    assert error == ""


def test_hello_word():
    code = _code(
        """
        var hello = "hello";
        print hello;
        print "world";
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == _lines("hello", "world")
    assert error == ""


def test_semicolon_error():
    code = _code(
        """
        var hello = "hello";
        print hello
        print "world";
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 65
    assert output == ""
    assert error.strip() == "[line 3] Error at 'print': Expect ';' after value."


def test_duplicate_declaration():
    code = _code(
        """
        fun bad() {
            var a = "first";
            var a = "second";
        }
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 65
    assert output == ""
    assert (
        error.strip()
        == "[line 3] Error at 'a': Already a variable with this name in this scope."
    )


def test_global_return():
    code = _code(
        """
        return 1;
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 65
    assert output == ""
    assert (
        error.strip() == "[line 1] Error at 'return': Can't return from top-level code."
    )


def test_simple_class():
    code = _code(
        """
        class Bacon {
            eat() {
                print "Crunch crunch crunch!";
            }
        }

        Bacon().eat(); // Prints "Crunch crunch crunch!".
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == "Crunch crunch crunch!"
    assert error == ""


def test_class_this():
    code = _code(
        """
        class Cake {
            taste() {
                var adjective = "delicious";
                print "The " + this.flavor + " cake is " + adjective + "!";
            }
        }

        var cake = Cake();
        cake.flavor = "German chocolate";
        cake.taste();
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == "The German chocolate cake is delicious!"
    assert error == ""


def test_class_binding():
    code = _code(
        """
        class Person {
            sayName() {
                print this.name;
            }
        }

        var jane = Person();
        jane.name = "Jane";

        var bill = Person();
        bill.name = "Bill";

        bill.sayName = jane.sayName;
        bill.sayName();
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0
    assert output.strip() == "Jane"
    assert error == ""


def test_this_outside_class():
    code = _code(
        """
        fun notAMethod() {
            print this;
        }
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 65
    assert output == ""
    assert (
        error.strip()
        == "[line 2] Error at 'this': Can't use 'this' outside of a class."
    )


def test_class_init():
    code = _code(
        """
        class Cake {
            init(adjective) {
                this.adjective = adjective;
                this.flavor = "German chocolate";
            }
            taste() {
                print "The " + this.flavor + " cake is " + this.adjective + "!";
            }
        }

        var cake = Cake("delicious");
        cake.taste();
        """
    )

    with _redirect() as (stdout, stderr):
        exit_code = main.run_text(Command.INTERPRET, code)

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert exit_code == 0, error
    assert output.strip() == "The German chocolate cake is delicious!"
    assert error == ""
