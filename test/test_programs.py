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


@contextmanager
def _redirect() -> Generator[tuple[io.StringIO, io.StringIO], None, None]:
    with io.StringIO() as stdout, redirect_stdout(stdout):
        with io.StringIO() as stderr, redirect_stderr(stderr):
            yield stdout, stderr


def _run(text: str) -> tuple[str, str, int]:
    with _redirect() as (stdout, stderr):
        try:
            exit_code = main.run_text(Command.INTERPRET, text)
        except Exception:
            exit_code = 1

        output = stdout.getvalue()
        error = stderr.getvalue()

    return output, error, exit_code


def _lines(*lines: Any) -> str:
    if len(lines) == 1 and isinstance(lines[0], Generator):
        lines = tuple(lines[0])
    return "\n".join(map(str, lines))


@cache
def _fib(n: int) -> int:
    if n <= 1:
        return n
    return _fib(n - 2) + _fib(n - 1)


def test_fib() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines(_fib(i) for i in range(20))
    assert error == ""


def test_closure() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines(1, 2, 3)
    assert error == ""


def test_shadowing() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines("global", "global")
    assert error == ""


def test_hello_word() -> None:
    code = _code(
        """
        var hello = "hello";
        print hello;
        print "world";
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines("hello", "world")
    assert error == ""


def test_semicolon_error() -> None:
    code = _code(
        """
        var hello = "hello";
        print hello
        print "world";
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 65, output
    assert output == ""
    assert error.strip() == "[line 3] Error at 'print': Expect ';' after value."


def test_duplicate_declaration() -> None:
    code = _code(
        """
        fun bad() {
            var a = "first";
            var a = "second";
        }
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 65, output
    assert output == ""
    assert (
        error.strip()
        == "[line 3] Error at 'a': Already a variable with this name in this scope."
    )


def test_global_return() -> None:
    code = _code(
        """
        return 1;
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 65, output
    assert output == ""
    assert (
        error.strip() == "[line 1] Error at 'return': Can't return from top-level code."
    )


def test_simple_class() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "Crunch crunch crunch!"
    assert error == ""


def test_class_this() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "The German chocolate cake is delicious!"
    assert error == ""


def test_class_binding() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "Jane"
    assert error == ""


def test_this_outside_class() -> None:
    code = _code(
        """
        fun notAMethod() {
            print this;
        }
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 65, output
    assert output == ""
    assert (
        error.strip()
        == "[line 2] Error at 'this': Can't use 'this' outside of a class."
    )


def test_class_init() -> None:
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
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "The German chocolate cake is delicious!"
    assert error == ""


def test_class_inheritance() -> None:
    code = _code(
        """
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }

        class BostonCream < Doughnut {}

        BostonCream().cook();
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "Fry until golden brown."
    assert error == ""


def test_class_super() -> None:
    code = _code(
        """
        class Doughnut {
            cook() {
                print "Fry until golden brown.";
            }
        }

        class BostonCream < Doughnut {
            cook() {
                super.cook();
                print "Pipe full of custard and coat with chocolate.";
            }
        }

        BostonCream().cook();
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines(
        "Fry until golden brown.", "Pipe full of custard and coat with chocolate."
    )
    assert error == ""


def test_super_on_subclass() -> None:
    code = _code(
        """
        class A {
            method() {
                print "A method";
            }
        }

        class B < A {
            method() {
                print "B method";
            }

            test() {
                super.method();
            }
        }

        class C < B {}

        C().test();
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == "A method"
    assert error == ""


def test_break() -> None:
    code = _code(
        """
        for (var i = 0; i < 10; i = i + 1) {
            print i;

            if (i > 3) {
                break;
            }
        }
        """
    )
    output, error, exit_code = _run(code)

    assert exit_code == 0, error
    assert output.strip() == _lines(0, 1, 2, 3, 4)
    assert error == ""
