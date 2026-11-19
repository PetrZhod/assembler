"""Разбор синтаксиса ассемблера."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


LOAD = "load"
READ = "read"
WRITE = "write"
SQRT = "sqrt"

CONSTANT_MIN = 0
CONSTANT_MAX = (1 << 10) - 1
ADDRESS_MIN = 0
ADDRESS_MAX = (1 << 24) - 1

LOAD_PATTERN = re.compile(
    r"^accumulator\s*=\s*(?P<value>\d+)$",
    re.IGNORECASE,
)
READ_PATTERN = re.compile(
    r"^accumulator\s*=\s*memory\s*\[\s*accumulator\s*\]$",
    re.IGNORECASE,
)
WRITE_PATTERN = re.compile(
    r"^memory\s*\[\s*(?P<address>\d+)\s*\]\s*=\s*"
    r"accumulator$",
    re.IGNORECASE,
)
SQRT_PATTERN = re.compile(
    r"^accumulator\s*=\s*sqrt\s*\(\s*accumulator\s*\)$",
    re.IGNORECASE,
)


class AssemblyError(ValueError):
    """Ошибка синтаксиса или диапазона."""


@dataclass(frozen=True)
class Instruction:
    """Команда во внутреннем представлении."""

    name: str
    fields: tuple[tuple[str, int], ...]
    source_line: int

    def field(self, name: str) -> int:
        """Вернуть значение поля команды."""
        for field_name, value in self.fields:
            if field_name == name:
                return value
        raise KeyError(name)

    def format_for_test(self) -> str:
        """Форматировать команду для тестов."""
        values = ", ".join(
            f"{name}={value}" for name, value in self.fields
        )
        return f"line={self.source_line}: {self.name}({values})"


def _check_range(
    name: str,
    value: int,
    minimum: int,
    maximum: int,
    line_number: int,
) -> int:
    """Проверить диапазон поля."""
    if not minimum <= value <= maximum:
        message = (
            f"строка {line_number}: поле {name} "
            f"должно быть в диапазоне {minimum}..{maximum}"
        )
        raise AssemblyError(message)
    return value


def _parse_decimal(
    token: str,
    line_number: int,
    field_name: str,
    minimum: int,
    maximum: int,
) -> int:
    """Преобразовать и проверить операнд."""
    try:
        value = int(token, 10)
    except ValueError as error:
        message = (
            f"строка {line_number}: поле {field_name} "
            "должно быть целым числом"
        )
        raise AssemblyError(message) from error
    return _check_range(field_name, value, minimum, maximum, line_number)


def _instruction_from_match(
    name: str,
    fields: tuple[tuple[str, int], ...],
    line_number: int,
) -> Instruction:
    """Создать команду из проверенных полей."""
    return Instruction(name, fields, line_number)


def _parse_load(line: str, line_number: int) -> Instruction | None:
    """Разобрать загрузку константы."""
    match = LOAD_PATTERN.fullmatch(line)
    if not match:
        return None
    value = _parse_decimal(
        match.group("value"),
        line_number,
        "B",
        CONSTANT_MIN,
        CONSTANT_MAX,
    )
    return _instruction_from_match(
        LOAD,
        (("A", 0), ("B", value)),
        line_number,
    )


def _parse_write(line: str, line_number: int) -> Instruction | None:
    """Разобрать запись в память."""
    match = WRITE_PATTERN.fullmatch(line)
    if not match:
        return None
    address = _parse_decimal(
        match.group("address"),
        line_number,
        "B",
        ADDRESS_MIN,
        ADDRESS_MAX,
    )
    return _instruction_from_match(
        WRITE,
        (("A", 1), ("B", address)),
        line_number,
    )


def _parse_line(line: str, line_number: int) -> Instruction:
    """Разобрать одну непустую строку."""
    load = _parse_load(line, line_number)
    if load is not None:
        return load
    if READ_PATTERN.fullmatch(line):
        return _instruction_from_match(READ, (("A", 7),), line_number)

    write = _parse_write(line, line_number)
    if write is not None:
        return write

    if SQRT_PATTERN.fullmatch(line):
        return _instruction_from_match(SQRT, (("A", 5),), line_number)

    message = (
        f"строка {line_number}: "
        f"неизвестное выражение {line!r}"
    )
    raise AssemblyError(message)


def parse_source(source: str) -> list[Instruction]:
    """Разобрать исходник."""
    instructions = []
    for line_number, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if line:
            instructions.append(_parse_line(line, line_number))
    return instructions


def format_program(instructions: Iterable[Instruction]) -> str:
    """Подготовить представление."""
    lines = ["IR:"]
    lines.extend(
        f"{index}: {instruction.format_for_test()}"
        for index, instruction in enumerate(instructions)
    )
    return "\n".join(lines)