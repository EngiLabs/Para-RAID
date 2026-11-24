from __future__ import annotations

import asyncio
from datetime import datetime
import os
from typing import Any

from httpx import AsyncClient, ConnectError
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import config as global_config
from cli.completer import create_cli_completer
from cli.parser import parse_command

import logging
logging.getLogger('httpx').disabled = True


console = Console()

CLI_STYLE = Style.from_dict({
    "prompt": "ansicyan bold",
    "bottom-toolbar": "bg:#222222 #ffffff",
    "bottom-toolbar.on": "#00ff00 bold",
    "bottom-toolbar.off": "#ff4444 bold",
    "bottom-toolbar.info": "#00d7ff",
})


class CLI:
    def __init__(self, host: str, port: int):
        connect_host = "127.0.0.1" if host in ("0.0.0.0", "", None) else host
        self.base_url = f"http://{connect_host}:{port}"
        self.client = AsyncClient(base_url=self.base_url, timeout=5.0)
        self.current_speed = 255
        self.latest_status: dict[str, Any] = {}
        self.server_online = False
        self._running = False
        self._bg_task: asyncio.Task | None = None

    async def start(self) -> None:
        self._running = True
        self._bg_task = asyncio.create_task(self._poll_status_loop())

    async def close(self) -> None:
        self._running = False
        if self._bg_task:
            self._bg_task.cancel()
        await self.client.aclose()

    async def _poll_status_loop(self) -> None:
        while self._running:
            try:
                resp = await self.client.get("/api/status")
                if resp.status_code == 200:
                    self.latest_status = resp.json()
                    self.server_online = True
                else:
                    self.server_online = False
            except:
                self.server_online = False
            await asyncio.sleep(5.)

    def get_bottom_toolbar(self) -> HTML:
        if not self.server_online:
            return HTML(
                ' <style class="bottom-toolbar.off">SERVER IS OFFLINE</style>'
                f' | URL: {self.base_url} '
            )

        connected = self.latest_status.get("connected", False)
        telem = self.latest_status.get("telemetry", {})
        pos = self.latest_status.get("position", {})
        gait = self.latest_status.get("current_gait", "unknown")

        unit_badge = (
            '<style class="bottom-toolbar.on">UNIT ONLINE</style>'
            if connected else
            '<style class="bottom-toolbar.off">UNIT OFFLINE</style>'
        )

        x = pos.get("x", 0.0)
        y = pos.get("y", 0.0)

        return HTML(
            f' {unit_badge}'
            f' | gait: <style class="bottom-toolbar.info">{gait}</style>'
            f' | position: ({x:.2f}, {y:.2f})'
            f' | speed: {self.current_speed} '
        )

    async def send_command(self, payload: dict[str, Any]) -> dict[str, Any]:
        resp = await self.client.post("/api/command", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def stop_robot(self) -> None:
        try:
            await self.send_command({"action": "stop"})
            console.print("[bold red]emergency stop has been casted[/bold red]")
        except Exception as e:
            console.print(f"[bold red]: {e}[/bold red]")

    async def capture_photo(self, save_path: str | None = None) -> None:
        try:
            await self.send_command({"action": "photo"})
            console.print("[cyan]request sent, awaiting response...[/cyan]")
            await asyncio.sleep(1.0)

            resp = await self.client.get("/api/photo")
            if resp.status_code == 200:
                if not save_path:
                    os.makedirs("captures", exist_ok=True)
                    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    save_path = os.path.join("captures", filename)

                with open(save_path, "wb") as f:
                    f.write(resp.content)
                console.print(f"[bold green][OK] successfully saved:[/bold green] [underline]{save_path}[/underline]")
            elif resp.status_code == 404:
                console.print("[yellow]there's no gathered shot, try again in a second[/yellow]")
            else:
                console.print(f"[red]photo gathering error: HTTP {resp.status_code}[/red]")
        except Exception as e:
            console.print(f"[bold red]photo error: {e}[/bold red]")

    @staticmethod
    def print_help() -> None:
        table = Table(title="available CLI commands:", border_style="cyan")
        table.add_column("cmd", style="bold green")
        table.add_column("xmpl", style="yellow")
        table.add_column("dscr", style="white")

        table.add_row(
            "forward / fwd / w",
            "forward 3m / fwd 50cm / w 2s / forward",
            "forward movement by distance (m, cm, mm), time (s, ms) or continuously",
        )
        table.add_row(
            "backward / bwd / s",
            "backward 4m / bwd 1s / s",
            "backward movement by distance (m, cm, mm), time (s, ms) or continuously",
        )
        table.add_row(
            "left / a",
            "left 1m / left 2s / a",
            "left shift",
        )
        table.add_row(
            "right / d",
            "right 1m / right 2s / d",
            "right shift",
        )
        table.add_row(
            "stop / halt / x / Ctrl+C",
            "",
            "immediatly stop all movements",
        )
        table.add_row(
            "speed",
            "speed 200",
            "set current movement speed (conventional units: 1-255)",
        )
        table.add_row(
            "gait",
            "gait walk, gait trot, gait creep",
            "switch the gait",
        )
        table.add_row(
            "home",
            "",
            "return servos to default position",
        )
        table.add_row(
            "relax",
            "",
            "relax servos",
        )
        table.add_row(
            "wake",
            "",
            "servos hold and power (!relax)",
        )
        table.add_row(
            "pose",
            "pose 0 0 0 ... (12 angles)",
            "set 12 joint angles in deg: RF, LF, RB, LB × (phi, alpha, beta)",
        )
        table.add_row(
            "led",
            "led on / led off",
            "LED controls",
        )
        table.add_row(
            "photo",
            "photo / photo my_shot.jpg",
            "request a photo and save it",
        )
        table.add_row(
            "goto",
            "goto 1.5 2.0",
            "proceeding a move to coordinates {X, Y}",
        )
        table.add_row(
            "status / telemetry",
            "",
            "telemetry debug print",
        )
        table.add_row(
            "help / ?",
            "",
            "show this page",
        )
        table.add_row(
            "exit / quit / Ctrl+D",
            "",
            "literally",
        )

        console.print(table)

    def print_status_details(self) -> None:
        if not self.server_online:
            console.print("[bold red]server is unreachable[/bold red]")
            return

        table = Table(title="unit telemetry", border_style="blue")
        table.add_column("key", style="cyan")
        table.add_column("value", style="bold white")

        connected = self.latest_status.get("connected", False)
        table.add_row("connection", "W" if connected else "L")

        telem = self.latest_status.get("telemetry", {})
        table.add_row("IR", str(telem.get("ir_sensors", [])))
        table.add_row(
            "IMU",
            f"R={telem.get('imu_roll', 0.0):.1f}° P={telem.get('imu_pitch', 0.0):.1f}° Y={telem.get('imu_yaw', 0.0):.1f}°",
        )
        table.add_row("IMU accel/gyro", f"{telem.get('imu_accel', [])} / {telem.get('imu_gyro', [])}")
        table.add_row("GAIT", str(self.latest_status.get("current_gait", "-")))

        pos = self.latest_status.get("position", {})
        table.add_row("(X, Y)", f"({pos.get('x', 0.0):.2f}, {pos.get('y', 0.0):.2f})")
        table.add_row("heading", f"{pos.get('heading', 0.0):.1f}°")
        table.add_row("has_frame flag", "ye" if self.latest_status.get("has_frame") else "nah")

        console.print(table)


async def run_cli() -> None:
    host = global_config.SERVER_HOST
    port = global_config.SERVER_PORT

    cli = CLI(host, port)
    await cli.start()

    console.print(Panel.fit(
        r"""[bold cyan]
 ____                       ____      _    ___ ____  
|  _ \ __ _ _ __ __ _      |  _ \    / \  |_ _|  _ \ 
| |_) / _` | '__/ _` |_____| |_) |  / _ \  | || | | |
|  __/ (_| | | | (_| |_____|  _ <  / ___ \ | || |_| |
|_|   \__,_|_|  \__,_|     |_| \_\/_/   \_\___|____/ 
[/bold cyan]
[bold white]PARA-Raid CLI[/bold white]
[dim]server is at [underline]""" + cli.base_url + r"""[/underline][/dim]
[dim][bold]help[/bold] = available commands[/dim]
""",
        border_style="cyan"
    ))

    session = PromptSession(
        history=InMemoryHistory(),
        auto_suggest=AutoSuggestFromHistory(),
        completer=create_cli_completer(),
        style=CLI_STYLE,
    )

    try:
        while True:
            try:
                user_input = await session.prompt_async(
                    HTML("<prompt>&gt;&gt;&gt; </prompt>"),
                    bottom_toolbar=cli.get_bottom_toolbar,
                )
            except KeyboardInterrupt:  # Ctrl+C
                await cli.stop_robot()
                continue
            except EOFError:  # Ctrl+D
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            try:
                cmd_data = parse_command(user_input, current_speed=cli.current_speed)
                if not cmd_data:
                    continue

                action = cmd_data.get("action")

                if action == "exit":
                    break
                elif action == "help":
                    cli.print_help()
                elif action == "status":
                    cli.print_status_details()
                elif action == "local_speed":
                    cli.current_speed = cmd_data["speed"]
                    console.print(f"[green]current speed is set to {cli.current_speed}[/green]")
                elif action == "photo":
                    await cli.capture_photo(cmd_data.get("save_path"))
                else:
                    res = await cli.send_command(cmd_data)
                    if res.get("status") == "ok":
                        if res.get("timed"):
                            dur = res.get("duration_s")
                            dist = res.get("distance_m")
                            dir_name = res.get("direction")
                            dist_str = f" ({dist}m)" if dist else ""
                            console.print(f"[bold green]> moving {dir_name}{dist_str} started (timeout: {dur}s)...[/bold green]")
                        else:
                            console.print(f"[green][OK]: {action}[/green]")
                    else:
                        console.print(f"[yellow][result]: {res}[/yellow]")

            except ValueError as ve:
                console.print(f"[bold red]input error:[/bold red] {ve}")
            except ConnectError:
                console.print(f"[bold red]connection error:[/bold red] can't connect to the server ({cli.base_url})")
            except Exception as e:
                console.print(f"[bold red]execution error:[/bold red] {e}")

    finally:
        await cli.close()
        console.print("[dim]CLI execution finished[/dim]")


if __name__ == "__main__":
    asyncio.run(run_cli())
