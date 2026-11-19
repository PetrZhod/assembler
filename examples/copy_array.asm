# Инициализация исходного массива по адресам 100..102.
accumulator = 11
memory[100] = accumulator
accumulator = 22
memory[101] = accumulator
accumulator = 33
memory[102] = accumulator

# Копирование массива по адресам 200..202.
accumulator = 100
accumulator = memory[accumulator]
memory[200] = accumulator
accumulator = 101
accumulator = memory[accumulator]
memory[201] = accumulator
accumulator = 102
accumulator = memory[accumulator]
memory[202] = accumulator