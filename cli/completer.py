from __future__ import annotations

from prompt_toolkit.completion import NestedCompleter


def create_cli_completer() -> NestedCompleter:
    dist_dur_completions = {
        "1m": None, "2m": None, "3m": None, "4m": None, "5m": None,
        "30cm": None, "50cm": None, "100cm": None,
        "1s": None, "2s": None, "3s": None, "5s": None,
    }

    return NestedCompleter.from_nested_dict({
        "forward": dist_dur_completions,
        "fwd": dist_dur_completions,
        "backward": dist_dur_completions,
        "bwd": dist_dur_completions,
        "left": dist_dur_completions,
        "right": dist_dur_completions,
        "stop": None,
        "halt": None,
        "speed": {"50": None, "100": None, "150": None, "200": None, "255": None},
        "gait": {
            "walk": None,
            "trot": None,
            "creep": None,
        },
        "home": None,
        "relax": None,
        "wake": None,
        "pose": None,
        "led": {
            "on": None,
            "off": None,
            "1": None,
            "0": None,
        },
        "photo": None,
        "goto": None,
        "status": None,
        "telemetry": None,
        "help": None,
        "exit": None,
        "quit": None,
    })
