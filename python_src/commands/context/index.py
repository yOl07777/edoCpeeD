from __future__ import annotations

import importlib

from python_src.commands.context.context import call as context


contextNonInteractive = importlib.import_module("python_src.commands.context.context-noninteractive").call
