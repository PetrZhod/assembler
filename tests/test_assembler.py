"""Тесты разбора исходника."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from assembler import AssemblyError, format_program, parse_source  # noqa: E402
from machine_code import encode_program, format_bytes  # noqa: E402


class AssemblerTests(unittest.TestCase):
    """Проверки синтаксиса и представления."""

    @staticmethod
    def field_values(instruction):
        """Получить поля команды словарём."""
        return dict(instruction.fields)

    def test_variant_10_commands_have_required_fields(self):
        program = """
        accumulator = 850
        accumulator = memory[accumulator]
        memory[392] = accumulator
        accumulator = sqrt(accumulator)
        """

        instructions = parse_source(program)

        self.assertEqual(
            [item.name for item in instructions],
            ["load", "read", "write", "sqrt"],
        )
        self.assertEqual(
            [self.field_values(item) for item in instructions],
            [
                {"A": 0, "B": 850},
                {"A": 7},
                {"A": 1, "B": 392},
                {"A": 5},
            ],
        )

    def test_comments_and_empty_lines_are_ignored(self):
        source = "# comment\n\n accumulator = 0 # trailing comment\n"
        instructions = parse_source(source)

        self.assertEqual(len(instructions), 1)
        self.assertEqual(self.field_values(instructions[0]), {"A": 0, "B": 0})

    def test_invalid_source_is_rejected(self):
        invalid_programs = (
            ("unknown", "неизвестное выражение"),
            ("accumulator = -1", "неизвестное выражение"),
            ("accumulator = 1024", "диапазоне 0..1023"),
            (
                "memory[-1] = accumulator",
                "неизвестное выражение",
            ),
            ("memory[16777216] = accumulator", "диапазоне"),
            (
                "accumulator = sqrt(1)",
                "неизвестное выражение",
            ),
        )
        for source, message in invalid_programs:
            with self.subTest(source=source):
                with self.assertRaisesRegex(AssemblyError, message):
                    parse_source(source)

    def test_test_mode_format_contains_fields_and_values(self):
        instructions = parse_source(
            "accumulator = 850\nmemory[392] = accumulator\n"
        )

        self.assertEqual(
            format_program(instructions).splitlines(),
            [
                "IR:",
                "0: line=1: load(A=0, B=850)",
                "1: line=2: write(A=1, B=392)",
            ],
        )

    def test_specification_bytes_are_exact(self):
        source = (
            "accumulator = 850\n"
            "accumulator = memory[accumulator]\n"
            "memory[392] = accumulator\n"
            "accumulator = sqrt(accumulator)\n"
        )

        binary = encode_program(parse_source(source))

        self.assertEqual(
            format_bytes(binary),
            "0x90, 0x1A, 0x07, 0x41, 0x0C, 0x00, 0x00, 0x05",
        )