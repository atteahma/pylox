from collections.abc import Sequence
from app.logger import Logger
from app.schema import Token


class Parser:
    _logger: Logger
    _tokens: list[Token]

    def __init__(self, _logger: Logger, _tokens: Sequence[Token]) -> None:
        self._logger = _logger
        self._tokens = list(self._tokens)
