# Ассемблер и интерпретатор УВМ

Практическая работа по конфигурационному управлению.
Выполняется вариант 10: разработка ассемблера и интерпретатора учебной
виртуальной машины.

В репозитории реализованы этапы 1–4:

- алгебраический язык ассемблера и промежуточное представление;
- трансляция команд в машинный код;
- интерпретатор, раздельная память и XML-дамп;
- вычисление квадратного корня в аккумуляторе.

## Синтаксис ассемблера

Одна команда записывается в отдельной строке. Пробелы вокруг операторов
не важны. После символа `#` начинается комментарий.

| Команда | Алгебраический синтаксис | Поля |
|---|---|---|
| Загрузка константы | `accumulator = B` | `A=0`, `B=0..1023` |
| Чтение памяти | `accumulator = memory[accumulator]` | `A=7` |
| Запись в память | `memory[B] = accumulator` | `A=1`, `B=0..16777215` |
| Квадратный корень | `accumulator = sqrt(accumulator)` | `A=5` |

Пример программы находится в `examples/variant10.asm`:

```text
accumulator = 850
accumulator = memory[accumulator]
memory[392] = accumulator
accumulator = sqrt(accumulator)
```

## Ассемблер

Требуется Python 3.10 или новее.

```sh
python3 src/main.py examples/variant10.asm build/program.bin --test
```

В Windows:

```bat
run.bat examples\variant10.asm build\program.bin --test
```

Ассемблер принимает путь к исходному файлу, путь к двоичному результату
и флаг тестирования. В тестовом режиме выводятся внутреннее представление
и байтовая последовательность:

```text
Ассемблировано команд: 4
IR:
0: line=2: load(A=0, B=850)
1: line=3: read(A=7)
2: line=4: write(A=1, B=392)
3: line=5: sqrt(A=5)
Bytes:
0x90, 0x1A, 0x07, 0x41, 0x0C, 0x00, 0x00, 0x05
```

Кодирование выполняется в little-endian. Проверочные команды дают ровно:

| Поля | Байты |
|---|---|
| `A=0, B=850` | `0x90, 0x1A` |
| `A=7` | `0x07` |
| `A=1, B=392` | `0x41, 0x0C, 0x00, 0x00` |
| `A=5` | `0x05` |

## Интерпретатор и XML-дамп

Интерпретатор принимает двоичную программу, путь XML-дампа и включительный
диапазон адресов памяти:

```sh
python3 src/interpreter.py build/program.bin build/memory.xml 100 202
```

Память команд хранится отдельно от памяти данных. Интерпретатор выполняет
загрузку константы, чтение и запись памяти, а также `sqrt`. Диапазон дампа
задаётся двумя последними аргументами, адреса включаются в результат.

Программа копирования массива находится в `examples/copy_array.asm`:

```sh
python3 src/main.py examples/copy_array.asm build/copy.bin
python3 src/interpreter.py build/copy.bin build/copy.xml 100 202
```

Дамп имеет вид:

```xml
<?xml version='1.0' encoding='utf-8'?>
<memory start="100" end="202">
  <cell address="100" value="11" />
</memory>
```

## Этап 4. Операция `sqrt`

Команда `accumulator = sqrt(accumulator)` вычисляет целочисленный квадратный
корень и сохраняет результат в аккумуляторе. Пример сохраняет `sqrt(81)` по
адресу `300`:

```powershell
python src/main.py examples/sqrt.asm build/sqrt.bin
python src/interpreter.py build/sqrt.bin build/sqrt.xml 300 300
Get-Content build/sqrt.xml
```

В XML ожидается значение `9` по адресу `300`.

## Структура репозитория

```text
README.md
.gitignore
Makefile
run.bat
run.sh
requirements-dev.txt
src/
    assembler.py
    interpreter.py
    machine.py
    machine_code.py
    main.py
    interpreter.py
tests/
    test_assembler.py
    test_machine.py
examples/
    copy_array.asm
    sqrt.asm
    variant10.asm
```

В репозиторий не добавляются бинарные файлы, архивы, кэш Python,
артефакты сборки и настройки редакторов. Они перечислены в `.gitignore`.

## Проверка

```sh
python3 -m unittest discover -s tests -v
```

Имена функций и переменных оформлены по PEP 8. Исходные строки Python
ограничены 80 символами, функции — 40 строками, а сложность функций
не превышает установленный предел.