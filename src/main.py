"""CLI ассемблера УВМ. На этапе 1 выполняется только разбор исходника."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from assembler import AssemblyError, format_program, parse_source


def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Разбор исходной программы УВМ в промежуточное представление"
    )
    parser.add_argument("source", type=Path, help="путь к исходному тексту")
    parser.add_argument(
        "output",
        type=Path,
        help="путь к будущему бинарному файлу (зарезервирован для этапа 2)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="напечатать поля и значения внутреннего представления",
    )
    return parser


def run(source_path: Path, output_path: Path, test_mode: bool) -> int:
    """Загрузить и разобрать программу."""
    del output_path
    try:
        source = source_path.read_text(encoding="utf-8")
        instructions = parse_source(source)
    except (OSError, AssemblyError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    if test_mode:
        print(format_program(instructions))
    else:
        print(f"Разобрано команд: {len(instructions)}")
    return 0


def main() -> int:
    """Запустить CLI."""
    args = create_parser().parse_args()
    return run(args.source, args.output, args.test)


if __name__ == "__main__":
    raise SystemExit(main())