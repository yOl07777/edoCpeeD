from __future__ import annotations

from .exit import call

exit = {
    "type": "local-jsx",
    "name": "exit",
    "aliases": ["quit"],
    "description": "Exit the REPL",
    "immediate": True,
    "call": call,
}

default = exit
