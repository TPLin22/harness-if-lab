"""StepCLI-specific rendering for the first two semantic surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hif.delivery import build_delivery_manifest


class StepCliDeliveryAdapter:
    """Compile semantic Item bindings into external delivery files.

    The adapter owns concrete StepCLI-facing paths.  The Item itself remains
    backend-neutral and only names ``project_file`` or ``user_message``.
    """

    name = "stepcli"
    version = "0.1.0"

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
        )
