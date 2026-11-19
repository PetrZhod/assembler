.PHONY: test run

test:
	python3 -m unittest discover -s tests -v

run:
	python3 src/main.py examples/variant10.asm build/program.bin --test