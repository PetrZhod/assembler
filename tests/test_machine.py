"""Тесты кодирования и базовых команд УВМ."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from assembler import parse_source  # noqa: E402
from machine import Machine  # noqa: E402
from machine_code import decode_instruction, encode_program  # noqa: E402


class MachineTests(unittest.TestCase):
    """Проверки кода и операций с памятью."""

    def test_decode_specification_bytes(self):
        binary = bytes.fromhex("90 1A 07 41 0C 00 00 05")

        instructions = []
        offset = 0
        while offset < len(binary):
            instruction, offset = decode_instruction(binary, offset)
            instructions.append(instruction)

        self.assertEqual(
            [item.name for item in instructions],
            ["load", "read", "write", "sqrt"],
        )
        self.assertEqual(instructions[0].field("B"), 850)
        self.assertEqual(instructions[2].field("B"), 392)

    def test_copy_program_uses_separate_data_memory(self):
        source = (
            "accumulator = 11\n"
            "memory[100] = accumulator\n"
            "accumulator = 22\n"
            "memory[101] = accumulator\n"
            "accumulator = 100\n"
            "accumulator = memory[accumulator]\n"
            "memory[200] = accumulator\n"
            "accumulator = 101\n"
            "accumulator = memory[accumulator]\n"
            "memory[201] = accumulator\n"
        )

        machine = Machine()
        machine.execute(encode_program(parse_source(source)))

        self.assertEqual(machine.data_memory[100], 11)
        self.assertEqual(machine.data_memory[101], 22)
        self.assertEqual(machine.data_memory[200], 11)
        self.assertEqual(machine.data_memory[201], 22)
        self.assertNotEqual(machine.instruction_memory, b"")
        self.assertEqual(machine.executed_commands, 10)

    def test_sqrt_saves_integer_result_in_memory(self):
        source = (
            "accumulator = 81\n"
            "accumulator = sqrt(accumulator)\n"
            "memory[300] = accumulator\n"
        )

        machine = Machine()
        machine.execute(encode_program(parse_source(source)))

        self.assertEqual(machine.data_memory[300], 9)

    def test_stage5_vectors_write_new_result_vectors(self):
        cases = (
            ("examples/sqrt_vector_1.asm", 200, range(1, 8)),
            ("examples/sqrt_vector_2.asm", 400, range(2, 9)),
            ("examples/sqrt_vector_3.asm", 600, range(9, 16)),
        )

        for filename, result_start, expected in cases:
            with self.subTest(filename=filename):
                source = Path(filename).read_text(encoding="utf-8")
                program = encode_program(parse_source(source))
                machine = Machine()
                machine.execute(program)
                actual = [
                    machine.data_memory[result_start + offset]
                    for offset in range(7)
                ]
                self.assertEqual(actual, list(expected))


if __name__ == "__main__":
    unittest.main()