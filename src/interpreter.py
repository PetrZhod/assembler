"""CLI-интерпретатор УВМ для этапа 3."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from xml.etree import ElementTree

from assembler import ADDRESS_MAX, ADDRESS_MIN
from machine import ExecutionError, Machine
from machine_code import MachineCodeError


def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов."""
    parser = argparse.ArgumentParser(
        description="Интерпретатор УВМ"
    )
    parser.add_argument(
        "program",
        type=Path,
        help="двоичная программа",
    )
    parser.add_argument("dump", type=Path, help="XML-файл дампа")
    parser.add_argument("start", type=int, help="начальный адрес")
    parser.add_argument("end", type=int, help="конечный адрес")
    return parser


def dump_memory(
    path: Path,
    memory: dict[int, int],
    start: int,
    end: int,
) -> None:
    """Сохранить диапазон памяти в XML."""
    if not ADDRESS_MIN <= start <= end <= ADDRESS_MAX:
        raise ValueError(
            f"диапазон должен быть в пределах "
            f"{ADDRESS_MIN}..{ADDRESS_MAX}"
        )
    root = ElementTree.Element(
        "memory",
        {"start": str(start), "end": str(end)},
    )
    for address in range(start, end + 1):
        ElementTree.SubElement(
            root,
            "cell",
            {"address": str(address), "value": str(memory.get(address, 0))},
        )
    tree = ElementTree.ElementTree(root)
    ElementTree.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def run(
    program_path: Path,
    dump_path: Path,
    start: int,
    end: int,
) -> int:
    """Выполнить программу и сохранить дамп."""
    try:
        program = program_path.read_bytes()
        machine = Machine()
        machine.execute(program)
        dump_path.parent.mkdir(parents=True, exist_ok=True)
        dump_memory(dump_path, machine.data_memory, start, end)
    except (OSError, MachineCodeError, ExecutionError, ValueError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print(f"Выполнено команд: {machine.executed_commands}")
    return 0


def main() -> int:
    """Запустить CLI."""
    args = create_parser().parse_args()
    return run(args.program, args.dump, args.start, args.end)


if __name__ == "__main__":
    raise SystemExit(main())