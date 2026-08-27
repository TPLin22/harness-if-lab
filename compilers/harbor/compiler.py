"""Compile a semantic Item variant into an external Harbor Pack.

The compiler copies a task reference into an output directory, projects only
the cleaned TaskSpec statement into ``instruction.md``, and emits a launch
configuration using Harbor's existing local-task, extra-instruction, and
agent-stage upload hook interfaces.  It does not import Harbor at run time.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from harnesses.stepcli.adapter import StepCliDeliveryAdapter
from hif.delivery import (
    DeliveryError,
    load_item_variant,
    load_task_spec,
    safe_relative_path,
    sha256_file,
    write_json,
)


class HarborPackError(DeliveryError):
    """Raised when a Harbor Pack cannot be created safely."""


_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(value: str, *, fallback: str = "pack") -> str:
    result = _SLUG_RE.sub("-", value).strip("-._")
    return result or fallback


def _job_name(item_id: str, variant: str) -> str:
    suffix = f"--{variant}"
    value = item_id if item_id.endswith(suffix) else f"{item_id}{suffix}"
    return _slug(value)


def _write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(value, allow_unicode=False, sort_keys=False), encoding="utf-8"
    )


def _copy_task(source: Path, destination: Path) -> None:
    source = source.resolve()
    if not source.is_dir():
        raise HarborPackError(f"Task directory does not exist: {source}")
    for required in ("task.toml", "instruction.md"):
        if not (source / required).is_file():
            raise HarborPackError(f"Task directory is missing {required}: {source}")
    if destination.exists():
        raise HarborPackError(f"Refusing to overwrite existing task destination: {destination}")
    shutil.copytree(source, destination, symlinks=False)


def _copy_project_files(delivery_dir: Path, task_dir: Path, manifest: dict[str, Any]) -> list[dict[str, str]]:
    uploads: list[dict[str, str]] = []
    project_files = manifest["surfaces"]["project_file"]["files"]
    for entry in project_files:
        source_rel = safe_relative_path(
            str(entry["pack_relative_source"]).removeprefix("delivery/"),
            context="project delivery source",
        )
        workspace_rel = safe_relative_path(
            str(entry["workspace_relative_path"]),
            context="project workspace path",
        )
        source = delivery_dir / source_rel
        if not source.is_file():
            raise HarborPackError(f"Missing generated project delivery file: {source}")
        target = task_dir / "environment" / workspace_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        uploads.append(
            {
                "source": workspace_rel,
                "target": str(entry["container_target_path"]),
            }
        )
        entry["task_environment_relative_path"] = f"environment/{workspace_rel}"
    return uploads


def _build_launch_config(
    *,
    output_dir: Path,
    task_dir: Path,
    manifest: dict[str, Any],
    agent_name: str,
    model_name: str,
    environment_type: str,
    workspace: str,
    agent_kwargs: dict[str, Any] | None,
    disable_verifier: bool,
) -> dict[str, Any]:
    user_fragments = manifest["surfaces"]["user_message"]["fragments"]
    config: dict[str, Any] = {
        "jobs_dir": str((output_dir / "jobs").resolve()),
        "job_name": _job_name(
            str(manifest["item"]["item_id"]), str(manifest["variant"])
        ),
        "n_attempts": 1,
        "n_concurrent_trials": 1,
        "quiet": False,
        "tasks": [{"path": str(task_dir.resolve())}],
        "extra_instruction_paths": [
            str((output_dir / fragment["pack_relative_path"]).resolve())
            for fragment in user_fragments
        ],
        "environment": {
            "type": environment_type,
            "force_build": False,
            "delete": True,
        },
        "agents": [
            {
                "name": agent_name,
                "model_name": model_name,
                "kwargs": {
                    "stepcli_workspace": workspace,
                    **(agent_kwargs or {}),
                },
            }
        ],
    }
    project_uploads = manifest["surfaces"]["project_file"]["files"]
    if project_uploads:
        config["environment"]["setup_hooks"] = [
            {
                "name": "upload_files",
                "stages": ["agent"],
                "kwargs": {"files": _build_upload_entries(project_uploads)},
            }
        ]
    if disable_verifier:
        config["verifier"] = {"disable": True}
    return config


def _build_upload_entries(project_files: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "source": str(entry["workspace_relative_path"]),
            "target": str(entry["container_target_path"]),
        }
        for entry in project_files
    ]


class HarborPackCompiler:
    """Create one immutable-once-referenced Harbor Pack directory."""

    version = "0.1.0"

    def compile(
        self,
        *,
        item_path: Path,
        rule_library_path: Path,
        task_spec_path: Path,
        task_dir: Path,
        output_root: Path,
        variant: str = "intervention",
        workspace: str = "/testbed",
        agent_name: str = "stepcli",
        model_name: str = "openai/REPLACE_ME",
        environment_type: str = "docker",
        agent_kwargs: dict[str, Any] | None = None,
        allow_unsupported: bool = False,
        disable_verifier: bool = False,
    ) -> Path:
        pair, item = load_item_variant(item_path, variant)
        task = load_task_spec(task_spec_path)
        if task["_task_id"] != pair["task_ref"]:
            raise HarborPackError(
                f"TaskSpec ID {task['_task_id']!r} does not match pair task_ref {pair['task_ref']!r}"
            )
        output_root = output_root.resolve()
        output_root.mkdir(parents=True, exist_ok=True)
        pack_name = _slug(str(item["item_id"]))
        pack_dir = output_root / pack_name
        if pack_dir.exists():
            raise HarborPackError(
                f"Refusing to overwrite existing Pack {pack_dir}; choose a new output root"
            )
        pack_dir.mkdir(parents=True)
        delivery_dir = pack_dir / "delivery"
        dataset_dir = pack_dir / "dataset"
        task_name = _slug(task["_task_id"].split("/", 1)[-1])
        generated_task_dir = dataset_dir / task_name

        _copy_task(task_dir, generated_task_dir)
        # The cleaned TaskSpec is the only model-visible task statement.
        (generated_task_dir / "instruction.md").write_text(
            task["_problem_statement"] + "\n", encoding="utf-8"
        )

        adapter = StepCliDeliveryAdapter()
        manifest = adapter.compile(
            item_path=item_path,
            rule_library_path=rule_library_path,
            task_spec_path=task_spec_path,
            output_dir=delivery_dir,
            variant=variant,
            workspace=workspace,
            allow_unsupported=allow_unsupported,
        )
        _copy_project_files(delivery_dir, generated_task_dir, manifest)
        # Rewrite the manifest after the Pack compiler adds its task projection.
        write_json(delivery_dir / "manifest.json", manifest)

        launch_config = _build_launch_config(
            output_dir=pack_dir,
            task_dir=generated_task_dir,
            manifest=manifest,
            agent_name=agent_name,
            model_name=model_name,
            environment_type=environment_type,
            workspace=workspace,
            agent_kwargs=agent_kwargs,
            disable_verifier=disable_verifier,
        )
        launch_path = pack_dir / "launch.yaml"
        _write_yaml(launch_path, launch_config)

        pack_metadata = {
            "format": "hif.harbor_pack",
            "format_version": 1,
            "compiler": "compilers/harbor/compiler.py",
            "compiler_version": self.version,
            "variant": variant,
            "item_id": item["item_id"],
            "task_ref": pair["task_ref"],
            "paths": {
                "task": str(generated_task_dir.relative_to(pack_dir)),
                "delivery_manifest": "delivery/manifest.json",
                "launch_config": "launch.yaml",
            },
            "hashes": {
                "item": sha256_file(item_path),
                "rules": sha256_file(rule_library_path),
                "task_spec": sha256_file(task_spec_path),
                "delivery_manifest": sha256_file(delivery_dir / "manifest.json"),
                "launch_config": sha256_file(launch_path),
            },
            "runtime_outputs": "external; configure jobs_dir/output_root per experiment",
        }
        write_json(pack_dir / "pack.json", pack_metadata)
        return pack_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--item", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--task-spec", type=Path, required=True)
    parser.add_argument("--task-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--variant", choices=("baseline", "intervention"), default="intervention")
    parser.add_argument("--workspace", default="/testbed")
    parser.add_argument("--agent", default="stepcli")
    parser.add_argument("--model", default="openai/REPLACE_ME")
    parser.add_argument("--environment-type", default="docker")
    parser.add_argument("--allow-unsupported", action="store_true")
    parser.add_argument("--disable-verifier", action="store_true")
    parser.add_argument(
        "--agent-kwargs-json",
        help="JSON object merged into the generated agent kwargs",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    kwargs: dict[str, Any] | None = None
    if args.agent_kwargs_json:
        value = json.loads(args.agent_kwargs_json)
        if not isinstance(value, dict):
            raise SystemExit("--agent-kwargs-json must decode to an object")
        kwargs = value
    try:
        pack = HarborPackCompiler().compile(
            item_path=args.item,
            rule_library_path=args.rules,
            task_spec_path=args.task_spec,
            task_dir=args.task_dir,
            output_root=args.output_root,
            variant=args.variant,
            workspace=args.workspace,
            agent_name=args.agent,
            model_name=args.model,
            environment_type=args.environment_type,
            agent_kwargs=kwargs,
            allow_unsupported=args.allow_unsupported,
            disable_verifier=args.disable_verifier,
        )
    except (DeliveryError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Pack compilation failed: {exc}") from exc
    print(pack)


if __name__ == "__main__":
    main()
