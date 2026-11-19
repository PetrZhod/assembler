"""Модель памяти и цикл выполнения УВМ."""

from __future__ import annotations

from dataclasses import dataclass, field
import math

from assembler import ADDRESS_MIN, LOAD, READ, SQRT, WRITE
from machine_code import DecodedInstruction, decode_instruction


class ExecutionError(RuntimeError):
    """Ошибка выполнения программы."""


@dataclass
class Machine:
    """УВМ с раздельной памятью."""

    instruction_memory: bytes = b""
    data_memory: dict[int, int] = field(default_factory=dict)
    accumulator: int = 0
    executed_commands: int = 0

    def _read_data(self, address: int) -> int:
        """Прочитать значение из памяти."""
        if address < ADDRESS_MIN:
            raise ExecutionError(
                "адрес памяти "
                "не может быть отрицательным"
            )
        return self.data_memory.get(address, 0)

    def _write_data(self, address: int, value: int) -> None:
        """Записать значение в память данных."""
        if address < ADDRESS_MIN:
            raise ExecutionError(
                "адрес памяти "
                "не может быть отрицательным"
            )
        self.data_memory[address] = value

    def _execute_basic(self, instruction: DecodedInstruction) -> None:
        """Выполнить базовую команду этапа 3."""
        if instruction.name == LOAD:
            self.accumulator = instruction.field("B")
            return
        if instruction.name == READ:
            self.accumulator = self._read_data(self.accumulator)
            return
        if instruction.name == WRITE:
            self._write_data(instruction.field("B"), self.accumulator)
            return
        if instruction.name == SQRT:
            self.accumulator = math.isqrt(self.accumulator)
            return
        raise ExecutionError(
            f"неизвестная команда: {instruction.name}"
        )

    def execute(self, program: bytes) -> None:
        """Выполнить программу полностью."""
        self.instruction_memory = bytes(program)
        offset = 0
        while offset < len(self.instruction_memory):
            instruction, offset = decode_instruction(
                self.instruction_memory,
                offset,
            )
            self._execute_basic(instruction)
            self.executed_commands += 1