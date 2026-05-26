from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def ModelPicker(*args: Any, **kwargs: Any) -> Any:
    selected = str(option(args, kwargs, "selected", option(args, kwargs, "model", scalar_arg(args, "deepseek-chat"))))
    models = normalize_items(option(args, kwargs, "models", ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]), text_key="name")
    for model in models:
        model["selected"] = model["name"] == selected
    return component_payload("model_picker", selected=selected, models=models, count=len(models))


__all__ = ["ModelPicker"]
