PY  := .venv/bin/𝜋thon
PIP := .venv/bin/pip

.PHONY: help start bot server


start:
	$(PY) startup.py

bot:
	$(PY) startup.py bot

server:
	$(PY) startup.py server

help:
	@echo helping hand

install:
	$(PIP) install -r requirements.txt
