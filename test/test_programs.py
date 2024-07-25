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

        var start_time = clock();

        for (var i = 0; i < 20; i = i + 1) {
            print fib(i);
        }
        """
    )

    with _redirect() as (stdout, stderr):
        assert main.run_text(Command.INTERPRET, code) == 0

        output = stdout.getvalue()
        error = stderr.getvalue()

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
        assert main.run_text(Command.INTERPRET, code) == 0

        output = stdout.getvalue()
        error = stderr.getvalue()

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
        assert main.run_text(Command.INTERPRET, code) == 0

        output = stdout.getvalue()
        error = stderr.getvalue()

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
        assert main.run_text(Command.INTERPRET, code) == 0

        output = stdout.getvalue()
        error = stderr.getvalue()

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
        assert main.run_text(Command.INTERPRET, code) == 65

        output = stdout.getvalue()
        error = stderr.getvalue()

    assert output == ""
    assert error.strip() == "[line 3] Error at 'print': Expect ';' after value."
