"""CLI ассемблера УВМ."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from assembler import AssemblyError, format_program, parse_source
from machine_code import encode_program, format_bytes


def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов."""
    parser = argparse.ArgumentParser(
        description="Ассемблер учебной машины"
    )
    parser.add_argument("source", type=Path, help="исходный файл")
    parser.add_argument("output", type=Path, help="двоичный файл")
    parser.add_argument(
        "--test",
        action="store_true",
        help="показать представление и байты",
    )
    return parser


def _read_instructions(source_path: Path):
    """Прочитать и разобрать исходник."""
    source = source_path.read_text(encoding="utf-8")
    return parse_source(source)


def assemble_file(
    source_path: Path,
    output_path: Path,
    test_mode: bool,
) -> int:
    """Ассемблировать файл и записать байты."""
    try:
        instructions = _read_instructions(source_path)
        binary = encode_program(instructions)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(binary)
    except (OSError, AssemblyError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    print(f"Ассемблировано команд: {len(instructions)}")
    if test_mode:
        print(format_program(instructions))
        print("Bytes:")
        print(format_bytes(binary))
    return 0


def main() -> int:
    """Запустить CLI."""
    args = create_parser().parse_args()
    return assemble_file(args.source, args.output, args.test)


if __name__ == "__main__":
    raise SystemExit(main())