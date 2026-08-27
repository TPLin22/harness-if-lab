#!/usr/bin/env python3
"""Assemble candidate multi-rule baseline/intervention pairs.

The output is a semantic Item plan.  This utility deliberately does not render
StepCLI configuration, create a Harbor task directory, or copy task/rule text
into a prompt.  It joins the checked-in task and canonical-rule references and
records enough matching metadata for a later compiler and adapter.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


FORMAT_VERSION = 0
CREATED_AT = "2026-08-27"
TASK_INDEX_REL = "benchmark/tasks/indexes/swebench-multilingual-pilot-20.yaml"
TASK_REVIEW_REL = "benchmark/tasks/indexes/swebench-multilingual-pilot-20-review.yaml"
RULE_LIBRARY_REL = "benchmark/rules/canonical/phase0-canonical.yaml"

SURFACES = (
    "system_prompt",
    "managed_instruction",
    "global_instruction",
    "project_file",
    "user_message",
    "tool_description",
    "skill",
)
ROLES = ("scored", "observed", "distractor")

# These assignments are intentionally conservative.  A tag match is enough to
# propose a binding, not enough to claim that a run will expose the opportunity.
PRIMARY_RULE = "rule-canon-p0-027"  # behavior_change + test_authoring
RUST_MATCH_RULE = "rule-canon-p0-041"  # rust_match_edit
RUST_API_RULE = "rule-canon-p0-040"  # rust_api_edit; judge-backed for now
COMMENT_RULE = "rule-canon-p0-039"  # code_comment_edit; subjective for now
DISTRACTOR_RULE = "rule-canon-p0-001"  # no run_style_checks tag in SWE specs

PRIMARY_SURFACES = ("project_file", "system_prompt", "user_message")


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently keeping the last value."""


def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key!r}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(
        value,
        allow_unicode=True,
        sort_keys=False,
        width=100,
        default_flow_style=False,
    ).encode("utf-8")


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=UniqueKeyLoader)


def load_rule_map(path: Path) -> dict[str, dict[str, Any]]:
    document = load_yaml(path)
    records = document.get("records", [])
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        rule_id = str(record["id"])
        if rule_id in result:
            raise ValueError(f"duplicate canonical rule: {rule_id}")
        result[rule_id] = record
    return result


def load_task_map(root: Path, index_path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    index = load_yaml(index_path)
    selected_ids = [str(value) for value in index.get("selected_ids", [])]
    if len(selected_ids) != len(set(selected_ids)):
        raise ValueError("task index contains duplicate selected IDs")
    result: dict[str, dict[str, Any]] = {}
    for entry in index.get("task_specs", []):
        path = root / str(entry["path"])
        if not path.is_file():
            raise FileNotFoundError(path)
        payload = path.read_bytes()
        actual_hash = sha256_bytes(payload)
        if actual_hash != entry["sha256"]:
            raise ValueError(f"task spec hash mismatch: {path}")
        spec = yaml.load(payload, Loader=UniqueKeyLoader)
        task_id = str(spec["task_id"])
        if task_id != str(entry["task_id"]):
            raise ValueError(f"task ID mismatch: {path}")
        if task_id in result:
            raise ValueError(f"duplicate task spec: {task_id}")
        spec["_index_sha256"] = actual_hash
        result[task_id] = spec
    return result, index


def load_review_flags(path: Path) -> tuple[dict[str, list[str]], str]:
    payload = path.read_bytes()
    document = yaml.safe_load(payload)
    flags: dict[str, list[str]] = {}
    for record in document.get("records", []):
        task_id = str(record["task_id"])
        if task_id in flags:
            raise ValueError(f"duplicate task review record: {task_id}")
        flags[task_id] = [str(flag) for flag in record.get("flags", [])]
    return flags, sha256_bytes(payload)


def opportunity_match(rule: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    required = [str(value) for value in rule.get("requires_opportunity", [])]
    offered = [
        str(value)
        for value in spec.get("curation", {}).get("offers_opportunity", [])
    ]
    offered_set = set(offered)
    matched = [value for value in required if value in offered_set]
    if not required:
        status = "not_required"
    elif len(matched) == len(required):
        status = "full"
    elif matched:
        status = "partial"
    else:
        status = "none"
    return {
        "required": required,
        "offered": offered,
        "matched": matched,
        "status": status,
        "derivation": "static_intersection_of_task_hints_and_rule_requirements",
    }


def authority_class(surface: str) -> str:
    if surface == "user_message":
        return "user_request"
    if surface in {"system_prompt", "managed_instruction", "global_instruction"}:
        return "general_instruction"
    return "project_context"


def choose_rule_specs(spec: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Return (rule_id, role, rationale) tuples in stable order."""

    tags = set(spec.get("curation", {}).get("offers_opportunity", []))
    choices: list[tuple[str, str, str]] = [
        (
            PRIMARY_RULE,
            "scored",
            "full opportunity match for behavior_change and test_authoring",
        )
    ]
    if "rust_match_edit" in tags:
        choices.append(
            (
                RUST_MATCH_RULE,
                "scored",
                "full opportunity match for rust_match_edit",
            )
        )
    if "rust_api_edit" in tags:
        choices.append(
            (
                RUST_API_RULE,
                "observed",
                "full opportunity match; judge-backed rule kept exploratory",
            )
        )
    if "code_comment_edit" in tags:
        choices.append(
            (
                COMMENT_RULE,
                "observed",
                "full opportunity match; subjective comment rationale review",
            )
        )
    if len(choices) == 1:
        choices.append(
            (
                DISTRACTOR_RULE,
                "distractor",
                "fixed attention-load distractor; no run_style_checks hint",
            )
        )
    return choices


def make_binding(
    rule: dict[str, Any],
    *,
    rule_id: str,
    role: str,
    rationale: str,
    surface: str,
    ordinal: int,
    match: dict[str, Any],
) -> dict[str, Any]:
    return {
        "binding_id": f"rb-{ordinal:02d}",
        "rule_ref": rule_id,
        "role": role,
        "target_surface": surface,
        "authority_class": authority_class(surface),
        "rendering_ref": None,
        "surface_fit": rule.get("surface_fit", {}).get(surface),
        "delivery_order": ordinal,
        "opportunity_match": match,
        "selection_rationale": rationale,
        "verification": {
            "status": "pending_verifier_implementation",
            "scoring_method": rule.get("scoring_method"),
            "verifiability": rule.get("verifiability"),
            "expected_evidence": list(rule.get("expected_evidence", [])),
        },
    }


def make_pair(
    *,
    task_id: str,
    spec: dict[str, Any],
    task_review_flags: list[str],
    rules: dict[str, dict[str, Any]],
    ordinal: int,
    task_index_sha256: str,
    task_review_sha256: str,
    rule_library_sha256: str,
    generator_sha256: str,
) -> dict[str, Any]:
    pair_id = f"swebench-multilingual-pilot-20--{spec['source']['instance_id']}"
    choices = choose_rule_specs(spec)
    bindings: list[dict[str, Any]] = []
    for binding_ordinal, (rule_id, role, rationale) in enumerate(choices, start=1):
        rule = rules[rule_id]
        surface = (
            PRIMARY_SURFACES[(ordinal - 1) % len(PRIMARY_SURFACES)]
            if binding_ordinal == 1
            else {
                RUST_MATCH_RULE: "project_file",
                RUST_API_RULE: "system_prompt",
                COMMENT_RULE: "skill",
                DISTRACTOR_RULE: "global_instruction",
            }[rule_id]
        )
        match = opportunity_match(rule, spec)
        binding = make_binding(
            rule,
            rule_id=rule_id,
            role=role,
            rationale=rationale,
            surface=surface,
            ordinal=binding_ordinal,
            match=match,
        )
        bindings.append(binding)

    scored = [binding for binding in bindings if binding["role"] == "scored"]
    must_scored = [
        binding
        for binding in scored
        if rules[binding["rule_ref"]].get("severity") == "must"
    ]
    surfaces = Counter(binding["target_surface"] for binding in bindings)
    return {
        "format": "hif.item_pair",
        "format_version": FORMAT_VERSION,
        "status": "candidate",
        "created_at": CREATED_AT,
        "pair_id": pair_id,
        "task_ref": task_id,
        "task_spec_sha256": spec["_index_sha256"],
        "rule_library_ref": RULE_LIBRARY_REL,
        "rule_library_sha256": rule_library_sha256,
        "authority_policy": {
            "id": "no_intentional_conflict_v0",
            "mode": "no_intentional_conflict",
            "precedence_held_constant_across_pair": True,
            "description": "Bindings are exploratory and non-conflicting by design; surface precedence is not inferred from serialization order.",
        },
        "tool_set_ref": None,
        "baseline": {
            "item_id": f"{pair_id}--baseline",
            "kind": "zero_injection",
            "task_ref": task_id,
            "rule_bindings": [],
            "difference_from_intervention": "omit all intervention rule bindings; keep task, policy, tool_set_ref, and runtime settings fixed",
        },
        "intervention": {
            "item_id": f"{pair_id}--intervention",
            "kind": "rule_injection",
            "task_ref": task_id,
            "rule_bindings": bindings,
            "difference_from_baseline": "rule_bindings_only",
        },
        "qualification": {
            "status": "candidate_pending_phase1_and_verifier_review",
            "task_review_flags": task_review_flags,
            "binding_count": len(bindings),
            "scored_binding_count": len(scored),
            "must_scored_binding_count": len(must_scored),
            "release_floor": {
                "require_at_least_one_must_scored_rule": True,
                "status": "unmet_candidate_warning" if not must_scored else "met",
                "reason": "The current SWE-bench panel exposes behavior/test opportunities but no reliable must-level workflow opportunity; do not promote until a task-specific must rule or an explicit exception is reviewed.",
            },
            "surface_support": "pending_stepcli_capability_review",
            "verifier_coverage": "pending_verifier_implementation",
            "leakage_check": "task_projection_allowlist_passed; pair contains references only and task review flags are propagated",
        },
        "provenance": {
            "task_index": TASK_INDEX_REL,
            "task_index_sha256": task_index_sha256,
            "task_review": TASK_REVIEW_REL,
            "task_review_sha256": task_review_sha256,
            "generator": "benchmark/items/generators/assemble_swebench_pilot.py",
            "generator_version": "0",
            "generator_sha256": generator_sha256,
        },
        "notes": [
            "This pair is a semantic candidate and is not a rendered prompt or StepCLI configuration.",
            "Roles and opportunity matches are curation metadata; runtime verdicts are produced later.",
        ],
        "_surface_counts": dict(sorted(surfaces.items())),
    }


def lint_pair(pair: dict[str, Any], rules: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if pair.get("format") != "hif.item_pair":
        errors.append("wrong pair format")
    if pair.get("tool_set_ref", "missing") is not None:
        errors.append("tool_set_ref must be null for this candidate panel")
    baseline = pair.get("baseline", {})
    intervention = pair.get("intervention", {})
    if baseline.get("task_ref") != pair.get("task_ref") or intervention.get("task_ref") != pair.get("task_ref"):
        errors.append("baseline/intervention task mismatch")
    if baseline.get("rule_bindings") != []:
        errors.append("baseline is not zero injection")
    item_ids = {
        str(baseline.get("item_id")),
        str(intervention.get("item_id")),
    }
    if len(item_ids) != 2 or "None" in item_ids:
        errors.append("baseline/intervention item IDs are missing or duplicated")
    seen: set[str] = set()
    seen_binding_ids: set[str] = set()
    for binding in intervention.get("rule_bindings", []):
        rule_id = str(binding.get("rule_ref"))
        if rule_id not in rules:
            errors.append(f"unknown rule reference: {rule_id}")
        if rule_id in seen:
            errors.append(f"duplicate rule binding without duplication group: {rule_id}")
        seen.add(rule_id)
        binding_id = str(binding.get("binding_id"))
        if binding_id in seen_binding_ids or binding_id == "None":
            errors.append(f"duplicate or missing binding ID: {binding_id}")
        seen_binding_ids.add(binding_id)
        if binding.get("role") not in ROLES:
            errors.append(f"invalid binding role: {binding.get('role')}")
        if binding.get("target_surface") not in SURFACES:
            errors.append(f"invalid target surface: {binding.get('target_surface')}")
        match = binding.get("opportunity_match", {})
        if binding.get("role") == "scored" and match.get("status") != "full":
            errors.append(f"scored binding lacks full opportunity match: {rule_id}")
        if binding.get("role") == "scored" and not match.get("required"):
            errors.append(f"scored binding has no declared opportunity requirement: {rule_id}")
        if binding.get("role") == "scored" and binding.get("surface_fit") in {None, "none", "low"}:
            errors.append(f"scored binding has insufficient surface fit: {rule_id}")
        # Semantic records must not grow backend-specific prompt/config fields.
        for value in binding.values():
            if isinstance(value, str) and re.search(r"(?:stepcli|claude\.md|codex\.md|--[a-z])", value, re.I):
                errors.append(f"backend-specific text in binding {rule_id}")
    # Pair records contain references and metadata, never task/rule prose or oracle fields.
    forbidden_keys = {"problem_statement", "statement", "patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"}
    def walk(value: Any, path: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in forbidden_keys:
                    errors.append(f"forbidden content key in pair: {path}/{key}")
                walk(child, f"{path}/{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}/{index}")
    walk(pair)
    return errors


def make_review_ledger(pairs: list[dict[str, Any]], pair_entries: list[dict[str, Any]]) -> dict[str, Any]:
    records = []
    for pair, entry in zip(pairs, pair_entries):
        q = pair["qualification"]
        flags = list(q["task_review_flags"])
        if q["release_floor"]["status"] == "unmet_candidate_warning":
            flags.append("no_must_scored_rule")
        if any(binding["role"] == "observed" for binding in pair["intervention"]["rule_bindings"]):
            flags.append("exploratory_observed_binding")
        records.append(
            {
                "pair_id": pair["pair_id"],
                "path": entry["path"],
                "sha256": entry["sha256"],
                "task_ref": pair["task_ref"],
                "decision": "retain_candidate",
                "flags": sorted(set(flags)),
                "binding_count": q["binding_count"],
                "scored_binding_count": q["scored_binding_count"],
                "note": "Static composition checks pass; verifier, surface capability, and release-floor review remain pending.",
            }
        )
    return {
        "format": "hif.item_review",
        "format_version": FORMAT_VERSION,
        "status": "completed_by_agent_pending_human_spot_check",
        "reviewed_at": CREATED_AT,
        "reviewer": "codex",
        "pair_count": len(records),
        "decision_summary": {
            "retained_candidate_count": len(records),
            "held_count": 0,
            "static_error_count": 0,
            "release_status": "none_released",
        },
        "criteria": [
            "one pair file has one TaskSpec reference and a zero-injection baseline",
            "intervention bindings reference existing canonical rules exactly once",
            "each binding has one role, one semantic target surface, and authority metadata",
            "scored bindings have a full static opportunity match",
            "pair data contains no task/rule prose or evaluator oracle fields",
            "baseline and intervention differ only in declared rule bindings",
            "tool_set_ref is reserved and null, with no StepCLI-specific mapping",
        ],
        "notes": [
            "This is an agent review for candidate-pipeline bring-up, not release approval.",
            "No must-severity scored rule is currently supported by a reliable task opportunity in this panel; every pair records that as a warning.",
            "Observed and distractor bindings are intentionally outside the primary denominator until verifiers and interference checks exist.",
        ],
        "records": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root")
    parser.add_argument("--output-dir", type=Path, default=Path("benchmark/items"), help="Item output directory")
    parser.add_argument("--overwrite", action="store_true", help="Replace generated candidate pair files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output_dir = (root / args.output_dir).resolve() if not args.output_dir.is_absolute() else args.output_dir
    task_index_path = root / TASK_INDEX_REL
    task_review_path = root / TASK_REVIEW_REL
    rule_library_path = root / RULE_LIBRARY_REL
    pair_dir = output_dir / "pairs" / "swebench-multilingual"
    generated_index = output_dir / "indexes" / "swebench-multilingual-pilot-20.yaml"
    generated_review = output_dir / "indexes" / "swebench-multilingual-pilot-20-review.yaml"
    if not args.overwrite and any(path.exists() for path in (pair_dir, generated_index, generated_review)):
        raise SystemExit("Generated Item records already exist; use --overwrite explicitly")
    tasks, task_index = load_task_map(root, task_index_path)
    review_flags, task_review_sha256 = load_review_flags(task_review_path)
    rules = load_rule_map(rule_library_path)
    required_rules = {PRIMARY_RULE, RUST_MATCH_RULE, RUST_API_RULE, COMMENT_RULE, DISTRACTOR_RULE}
    missing = required_rules - set(rules)
    if missing:
        raise SystemExit(f"canonical rules missing: {sorted(missing)}")
    index_payload = task_index_path.read_bytes()
    task_index_sha256 = sha256_bytes(index_payload)
    rule_library_sha256 = sha256_bytes(rule_library_path.read_bytes())
    generator_sha256 = sha256_bytes(Path(__file__).read_bytes())

    selected_ids = [f"swebench-multilingual/{instance_id}" for instance_id in task_index["selected_ids"]]
    if set(selected_ids) != set(tasks):
        raise ValueError("task index and spec map do not contain the same selected IDs")
    missing_review = set(selected_ids) - set(review_flags)
    if missing_review:
        raise ValueError(f"task review is missing selected IDs: {sorted(missing_review)}")
    pairs: list[dict[str, Any]] = []
    for ordinal, task_id in enumerate(selected_ids, start=1):
        pairs.append(
            make_pair(
                task_id=task_id,
                spec=tasks[task_id],
                task_review_flags=review_flags.get(task_id, []),
                rules=rules,
                ordinal=ordinal,
                task_index_sha256=task_index_sha256,
                task_review_sha256=task_review_sha256,
                rule_library_sha256=rule_library_sha256,
                generator_sha256=generator_sha256,
            )
        )
    errors: list[str] = []
    for pair in pairs:
        errors.extend(f"{pair['pair_id']}: {error}" for error in lint_pair(pair, rules))
    if errors:
        raise SystemExit("Item lint failed:\n" + "\n".join(errors))

    if args.overwrite and pair_dir.exists():
        for stale in pair_dir.glob("*.yaml"):
            stale.unlink()
    pair_dir.mkdir(parents=True, exist_ok=True)
    pair_entries: list[dict[str, Any]] = []
    for pair in pairs:
        instance_id = pair["task_ref"].split("/", 1)[1]
        path = pair_dir / f"{instance_id}.yaml"
        payload = yaml_bytes({key: value for key, value in pair.items() if not key.startswith("_")})
        path.write_bytes(payload)
        pair_entries.append(
            {
                "pair_id": pair["pair_id"],
                "path": str(path.relative_to(root)),
                "sha256": sha256_bytes(payload),
                "task_ref": pair["task_ref"],
                "binding_count": pair["qualification"]["binding_count"],
                "scored_binding_count": pair["qualification"]["scored_binding_count"],
            }
        )

    review = make_review_ledger(pairs, pair_entries)
    index = {
        "format": "hif.item_index",
        "format_version": FORMAT_VERSION,
        "status": "candidate_panel",
        "created_at": CREATED_AT,
        "task_panel_ref": TASK_INDEX_REL,
        "task_panel_sha256": task_index_sha256,
        "task_review_ref": TASK_REVIEW_REL,
        "task_review_sha256": task_review_sha256,
        "rule_library_ref": RULE_LIBRARY_REL,
        "rule_library_sha256": rule_library_sha256,
        "sampling": {
            "method": "ordered_task_panel_with_deterministic_rule_assignment",
            "generator": "benchmark/items/generators/assemble_swebench_pilot.py",
            "version": "0",
            "sha256": generator_sha256,
        },
        "pair_count": len(pair_entries),
        "pair_ids": [entry["pair_id"] for entry in pair_entries],
        "pairs": pair_entries,
        "surface_vocabulary": list(SURFACES),
        "role_vocabulary": list(ROLES),
        "tool_set_policy": "reserved_null_until_backend_capability_contract",
        "notes": [
            "Candidate semantic pair index; no pair is a released benchmark item.",
            "The generated baseline is zero injection. Rule-level causal claims require a more controlled design than this multi-rule panel.",
            "Pair files contain no rendered rule text and no StepCLI or Harbor configuration.",
        ],
    }
    index_dir = output_dir / "indexes"
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "swebench-multilingual-pilot-20.yaml").write_bytes(yaml_bytes(index))
    (index_dir / "swebench-multilingual-pilot-20-review.yaml").write_bytes(yaml_bytes(review))
    print(f"pairs={len(pairs)} output={pair_dir}")


if __name__ == "__main__":
    main()
