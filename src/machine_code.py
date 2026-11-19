"""Кодирование и декодирование команд УВМ."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from assembler import Instruction, LOAD, READ, SQRT, WRITE


BYTE_ORDER = "little"
OPCODE_BITS = 3
OPCODE_MASK = (1 << OPCODE_BITS) - 1
LOAD_SIZE = 2
READ_SIZE = 1
WRITE_SIZE = 4
SQRT_SIZE = 1
BYTE_FORMAT = "0x{:02X}"

OPCODES = {
    LOAD: 0,
    READ: 7,
    WRITE: 1,
    SQRT: 5,
}


class MachineCodeError(ValueError):
    """Ошибка машинного представления."""


@dataclass(frozen=True)
class DecodedInstruction:
    """Команда из машинного кода."""

    name: str
    fields: tuple[tuple[str, int], ...]

    def field(self, name: str) -> int:
        """Вернуть значение поля."""
        for field_name, value in self.fields:
            if field_name == name:
                return value
        raise KeyError(name)


def _encode_word(value: int, size: int) -> bytes:
    """Записать целое число в little-endian."""
    return value.to_bytes(size, BYTE_ORDER)


def encode_instruction(instruction: Instruction) -> bytes:
    """Преобразовать команду."""
    opcode = OPCODES[instruction.name]
    if instruction.name == LOAD:
        word = opcode | (instruction.field("B") << OPCODE_BITS)
        return _encode_word(word, LOAD_SIZE)
    if instruction.name == WRITE:
        word = opcode | (instruction.field("B") << OPCODE_BITS)
        return _encode_word(word, WRITE_SIZE)
    return bytes((opcode,))


def encode_program(instructions: Iterable[Instruction]) -> bytes:
    """Преобразовать программу в байты."""
    return b"".join(encode_instruction(item) for item in instructions)


def format_bytes(binary: bytes) -> str:
    """Вернуть байты в формате задания."""
    return ", ".join(BYTE_FORMAT.format(value) for value in binary)


def _read_word(program: bytes, offset: int, size: int) -> int:
    """Прочитать слово требуемого размера."""
    end = offset + size
    if end > len(program):
        raise MachineCodeError(
            "команда обрывается в конце файла"
        )
    return int.from_bytes(program[offset:end], BYTE_ORDER)


def decode_instruction(
    program: bytes,
    offset: int,
) -> tuple[DecodedInstruction, int]:
    """Декодировать команду."""
    if offset >= len(program):
        raise MachineCodeError(
            "счётчик команд вышел за "
            "границы файла"
        )
    opcode = program[offset] & OPCODE_MASK
    if opcode == OPCODES[READ]:
        return DecodedInstruction(READ, (("A", 7),)), offset + READ_SIZE
    if opcode == OPCODES[SQRT]:
        return DecodedInstruction(SQRT, (("A", 5),)), offset + SQRT_SIZE

    if opcode == OPCODES[LOAD]:
        word = _read_word(program, offset, LOAD_SIZE)
        value = word >> OPCODE_BITS
        return (
            DecodedInstruction(LOAD, (("A", 0), ("B", value))),
            offset + LOAD_SIZE,
        )

    if opcode == OPCODES[WRITE]:
        word = _read_word(program, offset, WRITE_SIZE)
        address = word >> OPCODE_BITS
        return (
            DecodedInstruction(WRITE, (("A", 1), ("B", address))),
            offset + WRITE_SIZE,
        )

    raise MachineCodeError(
        f"неизвестный код операции: {opcode}"
    )