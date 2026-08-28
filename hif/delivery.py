"""Shared loading and validation helpers for generated delivery plans.

The source benchmark records are semantic data.  This module only turns a
selected Item variant into a concrete, auditable set of files, message
fragments, and adapter-owned configuration records.  It deliberately has no
Harbor or StepCLI dependency.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

SUPPORTED_SURFACES = {
    "system_prompt",
    "managed_instruction",
    "global_instruction",
    "project_file",
    "user_message",
    "tool_description",
    "skill",
}
FIRST_STAGE_SURFACES = {"system_prompt", "project_file", "user_message"}
VARIANTS = {"baseline", "intervention"}
DELIVERY_FORMAT = "hif.delivery_manifest"
DELIVERY_FORMAT_VERSION = 1
TOOL_DESCRIPTION_MODES = {"append", "prepend", "replace"}
_SAFE_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")


class DeliveryError(ValueError):
    """Raised when semantic inputs cannot be compiled safely."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        .encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise DeliveryError(f"Unable to read YAML mapping {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DeliveryError(f"Expected a YAML mapping in {path}")
    return value


def _required_string(mapping: dict[str, Any], key: str, context: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DeliveryError(f"{context} requires a non-empty string field {key!r}")
    return value.strip()


def load_rule_statements(path: Path) -> dict[str, dict[str, Any]]:
    document = load_yaml_mapping(path)
    records = document.get("records")
    if not isinstance(records, list):
        raise DeliveryError(f"Rule library {path} has no records list")

    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            raise DeliveryError(f"Rule record {index} in {path} is not a mapping")
        rule_id = _required_string(raw, "id", f"Rule record {index}")
        statement = _required_string(raw, "statement", f"Rule {rule_id}")
        if rule_id in result:
            raise DeliveryError(f"Duplicate rule ID in {path}: {rule_id}")
        result[rule_id] = {"id": rule_id, "statement": statement, **raw}
    return result


def load_task_spec(path: Path) -> dict[str, Any]:
    document = load_yaml_mapping(path)
    task_id = _required_string(document, "task_id", f"Task spec {path}")
    content = document.get("content")
    if not isinstance(content, dict):
        raise DeliveryError(f"Task spec {path} has no content mapping")
    problem_statement = _required_string(
        content, "problem_statement", f"Task spec {task_id} content"
    )
    document["_task_id"] = task_id
    document["_problem_statement"] = problem_statement
    return document


def load_item_variant(path: Path, variant: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if variant not in VARIANTS:
        raise DeliveryError(
            f"Unknown Item variant {variant!r}; expected one of {sorted(VARIANTS)}"
        )
    document = load_yaml_mapping(path)
    if document.get("format") != "hif.item_pair":
        raise DeliveryError(
            f"{path} is not an hif.item_pair (got {document.get('format')!r})"
        )
    pair_id = _required_string(document, "pair_id", f"Item pair {path}")
    task_ref = _required_string(document, "task_ref", f"Item pair {pair_id}")
    selected = document.get(variant)
    if not isinstance(selected, dict):
        raise DeliveryError(f"Item pair {pair_id} has no {variant} mapping")
    item_id = _required_string(selected, "item_id", f"Item pair {pair_id}/{variant}")
    if selected.get("task_ref") != task_ref:
        raise DeliveryError(f"Item pair {pair_id}/{variant} task_ref disagrees with pair")
    bindings = selected.get("rule_bindings", [])
    if not isinstance(bindings, list):
        raise DeliveryError(f"Item {item_id} rule_bindings must be a list")
    return document, selected


_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def safe_binding_id(raw: Any, *, context: str) -> str:
    if not isinstance(raw, str) or not _SAFE_ID_RE.fullmatch(raw):
        raise DeliveryError(
            f"{context} has unsafe binding_id {raw!r}; use only letters, digits, '.', '_' and '-'")
    return raw


def safe_workspace_root(raw: str) -> str:
    value = raw.strip()
    if not value.startswith("/"):
        raise DeliveryError(f"StepCLI workspace must be an absolute POSIX path: {raw!r}")
    normalized = posixpath.normpath(value)
    if normalized == "/" or normalized.startswith("/../"):
        raise DeliveryError(f"Invalid StepCLI workspace path: {raw!r}")
    return normalized


def safe_relative_path(raw: str, *, context: str) -> str:
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise DeliveryError(f"{context} must be a relative path without '..': {raw!r}")
    normalized = path.as_posix()
    if normalized in {".", ""}:
        raise DeliveryError(f"{context} must not be empty")
    return normalized


def project_container_path(workspace: str, relative_path: str) -> str:
    root = safe_workspace_root(workspace)
    relative = safe_relative_path(relative_path, context="project file path")
    return posixpath.join(root, relative)


def _binding_surface(binding: dict[str, Any], context: str) -> str:
    surface = _required_string(binding, "target_surface", context)
    if surface not in SUPPORTED_SURFACES:
        raise DeliveryError(
            f"{context} uses unknown target surface {surface!r}; "
            f"expected one of {sorted(SUPPORTED_SURFACES)}"
        )
    return surface


def _delivery_order(binding: dict[str, Any], ordinal: int, context: str) -> int:
    value = binding.get("delivery_order", ordinal)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise DeliveryError(
            f"{context} requires delivery_order to be a positive integer"
        )
    return value


def _optional_safe_ref(raw: Any, *, context: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not _SAFE_REF_RE.fullmatch(raw.strip()):
        raise DeliveryError(
            f"{context} must be a non-empty reference using letters, digits, '.', '_', '/', or '-': {raw!r}"
        )
    return raw.strip()


def _binding_tool_refs(binding: dict[str, Any], *, context: str) -> list[str]:
    raw = binding.get("tool_refs")
    if raw is None:
        return []
    if not isinstance(raw, list) or not raw:
        raise DeliveryError(f"{context}.tool_refs must be a non-empty list")
    result: list[str] = []
    for index, value in enumerate(raw):
        result.append(
            _optional_safe_ref(value, context=f"{context}.tool_refs[{index}]")
            or ""
        )
    if any(not value for value in result) or len(result) != len(set(result)):
        raise DeliveryError(f"{context}.tool_refs must contain unique references")
    return result


def _description_mode(binding: dict[str, Any], *, context: str) -> str:
    value = binding.get("description_mode", "append")
    if not isinstance(value, str) or value.strip().lower() not in TOOL_DESCRIPTION_MODES:
        raise DeliveryError(
            f"{context}.description_mode must be append, prepend, or replace"
        )
    return value.strip().lower()


def _stepcli_surface_config(
    *,
    tool_set_ref: str | None,
    tool_description_overrides: dict[str, dict[str, str]],
    tool_set_projections: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Resolve the adapter-owned StepCLI projection and its audit record."""

    if tool_set_ref is None:
        if tool_description_overrides:
            return None, {
                "requested_ref": None,
                "status": "unsupported",
                "reason": "tool_description bindings require an explicit tool_set_ref",
            }
        return None, {"requested_ref": None, "status": "native_default"}

    projection = tool_set_projections.get(tool_set_ref)
    if projection is None:
        return None, {
            "requested_ref": tool_set_ref,
            "status": "unsupported",
            "reason": "no StepCLI adapter projection is registered for this tool set",
        }

    surface_name = projection.get("active")
    projected_refs = projection.get("tool_refs")
    if (
        not isinstance(surface_name, str)
        or not surface_name.strip()
        or not isinstance(projected_refs, dict)
    ):
        raise DeliveryError(
            f"Malformed StepCLI tool-set projection for {tool_set_ref!r}"
        )
    surface_name = surface_name.strip()
    resolved_tool_refs = {
        str(ref): str(model_name)
        for ref, model_name in sorted(projected_refs.items())
        if isinstance(ref, str) and isinstance(model_name, str)
    }
    if len(resolved_tool_refs) != len(projected_refs):
        raise DeliveryError(
            f"Malformed tool reference mapping for StepCLI tool set {tool_set_ref!r}"
        )
    tools: dict[str, Any] = {}
    if tool_description_overrides:
        tools["descriptionOverrides"] = {
            name: dict(override)
            for name, override in tool_description_overrides.items()
        }
    selection: dict[str, Any] = {}
    if tools:
        selection["tools"] = tools
    config: dict[str, Any] = {
        "active": surface_name,
        "surfaces": {surface_name: selection},
    }
    return config, {
        "requested_ref": tool_set_ref,
        "status": "planned",
        "adapter_projection": "harnesses/stepcli/adapter.py",
        "active_surface": surface_name.strip(),
        "resolved_tool_refs": resolved_tool_refs,
        "resolved_tool_names": sorted(set(resolved_tool_refs.values())),
        "description_override_tool_names": sorted(tool_description_overrides),
    }


def build_delivery_manifest(
    *,
    item_path: Path,
    rule_library_path: Path,
    task_spec_path: Path,
    output_dir: Path,
    variant: str = "intervention",
    workspace: str = "/testbed",
    allow_unsupported: bool = False,
    tool_set_projections: dict[str, dict[str, Any]] | None = None,
    adapter_version: str = "0.1.0",
) -> dict[str, Any]:
    """Render first-stage surfaces and return the written delivery manifest.

    ``output_dir`` is a delivery directory owned by a generated Pack.  The
    function writes one file per binding so each rule remains independently
    auditable.  It never mutates the semantic Item, rule library, or TaskSpec.
    """

    pair, item = load_item_variant(item_path, variant)
    rules = load_rule_statements(rule_library_path)
    task = load_task_spec(task_spec_path)
    pair_task_ref = _required_string(pair, "task_ref", f"Item pair {item_path}")
    if task["_task_id"] != pair_task_ref:
        raise DeliveryError(
            f"TaskSpec {task_spec_path} ID {task['_task_id']!r} does not match "
            f"Item task_ref {pair_task_ref!r}"
        )
    workspace = safe_workspace_root(workspace)

    bindings = item.get("rule_bindings", [])
    seen_binding_ids: set[str] = set()
    deliveries: list[dict[str, Any]] = []
    system_fragments: list[dict[str, Any]] = []
    system_prompt_parts: dict[str, str] = {}
    user_fragments: list[dict[str, Any]] = []
    project_files: list[dict[str, Any]] = []
    tool_description_overrides: dict[str, dict[str, str]] = {}
    unsupported: list[dict[str, Any]] = []
    seen_delivery_orders: dict[int, str] = {}
    tool_set_ref = _optional_safe_ref(
        pair.get("tool_set_ref"),
        context=f"Item pair {pair.get('pair_id', item_path)}.tool_set_ref",
    )

    for ordinal, raw_binding in enumerate(bindings, start=1):
        if not isinstance(raw_binding, dict):
            raise DeliveryError(f"Item {item['item_id']} binding {ordinal} is not a mapping")
        context = f"Item {item['item_id']} binding {ordinal}"
        binding_id = safe_binding_id(raw_binding.get("binding_id"), context=context)
        if binding_id in seen_binding_ids:
            raise DeliveryError(f"Duplicate binding_id in Item {item['item_id']}: {binding_id}")
        seen_binding_ids.add(binding_id)
        rule_ref = _required_string(raw_binding, "rule_ref", context)
        rule = rules.get(rule_ref)
        if rule is None:
            raise DeliveryError(f"{context} references unknown rule {rule_ref!r}")
        surface = _binding_surface(raw_binding, context)
        role = _required_string(raw_binding, "role", context)
        delivery_order = _delivery_order(raw_binding, ordinal, context)
        tool_refs = _binding_tool_refs(raw_binding, context=context)
        description_mode = (
            _description_mode(raw_binding, context=context)
            if surface == "tool_description"
            else None
        )
        if surface != "tool_description" and "tool_refs" in raw_binding:
            raise DeliveryError(
                f"{context}.tool_refs is only valid for tool_description bindings"
            )
        if surface != "tool_description" and "description_mode" in raw_binding:
            raise DeliveryError(
                f"{context}.description_mode is only valid for tool_description bindings"
            )
        if surface == "tool_description" and not tool_refs:
            raise DeliveryError(
                f"{context} targeting tool_description requires tool_refs"
            )
        previous_binding = seen_delivery_orders.get(delivery_order)
        if previous_binding is not None:
            raise DeliveryError(
                f"Item {item['item_id']} reuses delivery_order {delivery_order} "
                f"for bindings {previous_binding!r} and {binding_id!r}"
            )
        seen_delivery_orders[delivery_order] = binding_id
        content = rule["statement"].strip() + "\n"
        content_hash = sha256_bytes(content.encode("utf-8"))
        record: dict[str, Any] = {
            "binding_id": binding_id,
            "rule_ref": rule_ref,
            "role": role,
            "intended_surface": surface,
            "actual_surface": surface if surface in FIRST_STAGE_SURFACES else None,
            "status": "planned" if surface in FIRST_STAGE_SURFACES else "unsupported_surface",
            "content_sha256": content_hash,
            "content_bytes": len(content.encode("utf-8")),
            "delivery_order": delivery_order,
        }
        if tool_refs:
            record["tool_refs"] = tool_refs
        if description_mode is not None:
            record["description_mode"] = description_mode

        if surface == "system_prompt":
            relative = f"system_prompts/{binding_id}.md"
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            record.update(
                {
                    "transport": "harbor.agents[0].kwargs.stepcli_instruction_prompt",
                    "pack_relative_path": f"delivery/{relative}",
                }
            )
            system_fragments.append(
                {
                    "binding_id": binding_id,
                    "pack_relative_path": f"delivery/{relative}",
                    "content_sha256": content_hash,
                    "delivery_order": delivery_order,
                }
            )
            system_prompt_parts[binding_id] = content.strip()
        elif surface == "user_message":
            relative = f"user_messages/{binding_id}.md"
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            record.update(
                {
                    "transport": "harbor.extra_instruction_paths",
                    "pack_relative_path": f"delivery/{relative}",
                }
            )
            user_fragments.append(
                {
                    "binding_id": binding_id,
                    "pack_relative_path": f"delivery/{relative}",
                    "content_sha256": content_hash,
                    "delivery_order": delivery_order,
                }
            )
        elif surface == "project_file":
            project_relative = f".claude/rules/hif-{binding_id}.md"
            relative = f"project_files/{binding_id}.md"
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            target = project_container_path(workspace, project_relative)
            record.update(
                {
                    "transport": "harbor.environment.setup_hooks.upload_files",
                    "pack_relative_path": f"delivery/{relative}",
                    "workspace_relative_path": project_relative,
                    "container_target_path": target,
                }
            )
            project_files.append(
                {
                    "binding_id": binding_id,
                    "pack_relative_source": f"delivery/{relative}",
                    "workspace_relative_path": project_relative,
                    "container_target_path": target,
                    "content_sha256": content_hash,
                    "delivery_order": delivery_order,
                }
            )
        elif surface == "tool_description":
            # The actual model-visible names are resolved below once the
            # selected tool-set projection is known.  Keep this record
            # independent so an unsupported projection is auditable.
            record["transport"] = (
                "stepcli.extensions.surface.surfaces.<active>.tools.descriptionOverrides"
            )
        else:
            unsupported.append(
                {
                    "binding_id": binding_id,
                    "rule_ref": rule_ref,
                    "intended_surface": surface,
                    "status": "unsupported_surface",
                }
            )
            if not allow_unsupported:
                raise DeliveryError(
                    f"{context} targets unsupported first-stage surface {surface!r}; "
                    "pass allow_unsupported only for an explicitly partial exploratory Pack"
                )

        deliveries.append(record)

    # Resolve the semantic tool references only in the backend adapter.  The
    # Item never stores StepCLI names such as ``bash`` or ``str_replace_editor``.
    projections = tool_set_projections or {}
    projection = (
        projections.get(tool_set_ref)
        if tool_set_ref is not None
        else None
    )
    tool_description_records = [
        record
        for record in deliveries
        if record["intended_surface"] == "tool_description"
    ]
    for record in tool_description_records:
        refs = list(record.get("tool_refs", []))
        if projection is None:
            record["status"] = "unsupported_surface"
            unsupported.append(
                {
                    "binding_id": record["binding_id"],
                    "rule_ref": record["rule_ref"],
                    "intended_surface": "tool_description",
                    "status": "unsupported_surface",
                    "reason": (
                        "tool_description requires a registered StepCLI tool-set "
                        "projection"
                    ),
                }
            )
            continue

        resolved_names: list[str] = []
        unresolved = []
        for ref in refs:
            model_name = projection.get("tool_refs", {}).get(ref)
            if not isinstance(model_name, str):
                unresolved.append(ref)
            else:
                resolved_names.append(model_name)
        if unresolved:
            record["status"] = "unsupported_surface"
            unsupported.append(
                {
                    "binding_id": record["binding_id"],
                    "rule_ref": record["rule_ref"],
                    "intended_surface": "tool_description",
                    "status": "unsupported_surface",
                    "reason": f"unknown tool_refs for selected tool set: {unresolved}",
                }
            )
            continue

        if len(resolved_names) != len(set(resolved_names)):
            raise DeliveryError(
                f"Item {item['item_id']} maps multiple tool_refs to the same "
                f"model tool in binding {record['binding_id']}: {resolved_names}"
            )

        duplicate_names = [
            name for name in resolved_names if name in tool_description_overrides
        ]
        if duplicate_names:
            raise DeliveryError(
                f"Item {item['item_id']} targets the same model tool more than once "
                f"in tool_description bindings: {duplicate_names}"
            )
        mode = str(record["description_mode"])
        tool_description_records_for_rule = {
            name: {"mode": mode, "text": rules[record["rule_ref"]]["statement"].strip()}
            for name in resolved_names
        }
        tool_description_overrides.update(tool_description_records_for_rule)
        record["actual_surface"] = "tool_description"
        record["status"] = "planned"
        record["resolved_tool_names"] = resolved_names

    stepcli_surface_config, tool_set_record = _stepcli_surface_config(
        tool_set_ref=tool_set_ref,
        tool_description_overrides=tool_description_overrides,
        tool_set_projections=projections,
    )
    unresolved_tool_description = [
        entry
        for entry in unsupported
        if entry.get("intended_surface") == "tool_description"
    ]
    if unresolved_tool_description and not allow_unsupported:
        first = unresolved_tool_description[0]
        raise DeliveryError(
            f"Item {item['item_id']} binding {first['binding_id']} targets an "
            f"unsupported tool_description mapping: {first.get('reason', 'unknown reason')}"
        )
    if tool_set_record["status"] == "unsupported":
        if not allow_unsupported:
            raise DeliveryError(
                f"Item {item['item_id']} requests unsupported StepCLI tool set "
                f"{tool_set_ref!r}: {tool_set_record.get('reason', 'unknown reason')}"
            )
        for record in deliveries:
            if record["intended_surface"] == "tool_description":
                record["status"] = "unsupported_surface"
        for entry in tool_description_records:
            if not any(
                item.get("binding_id") == entry["binding_id"]
                for item in unsupported
            ):
                unsupported.append(
                    {
                        "binding_id": entry["binding_id"],
                        "rule_ref": entry["rule_ref"],
                        "intended_surface": "tool_description",
                        "status": "unsupported_surface",
                        "reason": tool_set_record.get("reason"),
                    }
                )

    deliveries.sort(key=lambda entry: entry["delivery_order"])
    system_fragments.sort(key=lambda entry: entry["delivery_order"])
    merged_system_prompt = "\n\n".join(
        system_prompt_parts[fragment["binding_id"]]
        for fragment in system_fragments
    )
    user_fragments.sort(key=lambda entry: entry["delivery_order"])
    project_files.sort(key=lambda entry: entry["delivery_order"])

    manifest: dict[str, Any] = {
        "format": DELIVERY_FORMAT,
        "format_version": DELIVERY_FORMAT_VERSION,
        "backend": "harbor",
        "harness": "stepcli",
        "variant": variant,
        "item": {
            "pair_id": _required_string(pair, "pair_id", f"Item pair {item_path}"),
            "item_id": item["item_id"],
            "task_ref": pair_task_ref,
            "tool_set_ref": tool_set_ref,
        },
        "task": {
            "task_spec_path": str(task_spec_path),
            "task_spec_sha256": sha256_file(task_spec_path),
            "task_id": task["_task_id"],
            "instruction_source": "TaskSpec.content.problem_statement",
            "instruction_sha256": sha256_bytes(
                task["_problem_statement"].encode("utf-8")
            ),
        },
        "surfaces": {
            "system_prompt": {
                "transport": "harbor.agents[0].kwargs.stepcli_instruction_prompt",
                "merge_strategy": "ordered_join_double_newline",
                "fragments": system_fragments,
                "merged_content_sha256": (
                    sha256_bytes(merged_system_prompt.encode("utf-8"))
                    if merged_system_prompt
                    else None
                ),
                "merged_content_bytes": len(merged_system_prompt.encode("utf-8")),
            },
            "user_message": {
                "base_task_instruction": "task/instruction.md",
                "transport": "harbor.extra_instruction_paths",
                "fragments": user_fragments,
            },
            "project_file": {
                "workspace_root": workspace,
                "discovery_expectation": "StepCLI project instruction discovery",
                "files": project_files,
            },
            "tool_description": {
                "transport": (
                    "stepcli.extensions.surface.surfaces.<active>.tools."
                    "descriptionOverrides"
                ),
                "bindings": [
                    entry
                    for entry in deliveries
                    if entry["intended_surface"] == "tool_description"
                ],
            },
        },
        "tool_set": tool_set_record,
        "harness_config": {
            "stepcli": {
                "extension_surface": stepcli_surface_config,
            }
        },
        "deliveries": deliveries,
        "unsupported": unsupported,
        "provenance": {
            "item_path": str(item_path),
            "item_sha256": sha256_file(item_path),
            "rule_library_path": str(rule_library_path),
            "rule_library_sha256": sha256_file(rule_library_path),
            "adapter": "harnesses/stepcli/adapter.py",
            "adapter_version": adapter_version,
        },
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest
