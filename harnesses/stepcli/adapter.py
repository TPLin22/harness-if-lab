"""StepCLI-specific rendering for semantic surfaces and tool factors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hif.delivery import build_delivery_manifest

# The semantic Item names stable roles (``shell``, ``editor``); this adapter
# owns the translation to concrete StepCLI model-visible tool names.  A later
# harness adapter can provide a different projection for the same Item.
STEPCLI_TOOL_SET_PROJECTIONS: dict[str, dict[str, Any]] = {
    "dsh_minimal": {
        "active": "dsh_minimal",
        "tool_refs": {
            "shell": "bash",
            "editor": "str_replace_editor",
        },
    }
}


class StepCliDeliveryAdapter:
    """Compile semantic Item bindings into external delivery files.

    The adapter owns concrete StepCLI-facing paths and tool-name projections.
    The Item itself remains backend-neutral and only names semantic surfaces
    and abstract tool references.
    """

    name = "stepcli"
    version = "0.2.0"

    def compile(
        self,
        *,
        item_path: Path,
        rule_library_path: Path,
        task_spec_path: Path,
        output_dir: Path,
        variant: str = "intervention",
        workspace: str = "/testbed",
        allow_unsupported: bool = False,
    ) -> dict[str, Any]:
        output_dir.mkdir(parents=True, exist_ok=True)
        return build_delivery_manifest(
            item_path=item_path,
            rule_library_path=rule_library_path,
            task_spec_path=task_spec_path,
            output_dir=output_dir,
            variant=variant,
            workspace=workspace,
            allow_unsupported=allow_unsupported,
            tool_set_projections=STEPCLI_TOOL_SET_PROJECTIONS,
            adapter_version=self.version,
        )
