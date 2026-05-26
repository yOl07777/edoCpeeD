from __future__ import annotations

from typing import Any

from ._nodes import render_node


def ErrorOverview(*errors: Any, **props: Any) -> dict[str, Any]:
    prop_errors = props.pop("errors", None)
    values = list(prop_errors if isinstance(prop_errors, (list, tuple)) else ([prop_errors] if prop_errors else []))
    values.extend(errors)
    normalized = [str(getattr(error, "message", error)) for error in values if error is not None]
    return render_node(
        "error_overview",
        errors=normalized,
        count=len(normalized),
        title=props.pop("title", "Errors"),
        style=props,
    )


default = ErrorOverview
_module_migration_placeholder = ErrorOverview
