PY := .venv/bin/𝜋thon

.PHONY: help start bot server


start:
	$(PY) startup.py

bot:
	$(PY) startup.py bot

server:
	$(PY) startup.py server

help:
	@echo helping hand
