import asyncio
from cli import run_cli


if __name__ == "__main__":
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt, SystemExit:
        exit(0)
