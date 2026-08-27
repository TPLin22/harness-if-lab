#!/usr/bin/env python3
"""Collect a small, reproducible SWE-bench Multilingual TaskSpec panel.

This utility deliberately stops at thin semantic task records.  It never
creates Harbor task directories, copies repositories, or writes the upstream
patch/test oracle into the repository.  The ``datasets`` package is loaded only
when the command is run; the development environment used for the first
collection is Harbor's environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import yaml


DATASET_NAME = "SWE-bench/SWE-bench_Multilingual"
DATASET_CONFIG = "default"
DATASET_SPLIT = "test"
DATASET_REVISION = "e5c585e008e2cb5eecc7c64192d855c53279d788"
COLLECTION_DATE = "2026-08-27"
SEED = 260827
FORMAT_VERSION = 0
MAX_CLEANED_STATEMENT_CHARS = 6000

# The adapter's map is copied as data rather than imported from Harbor.  This
# keeps the semantic collection utility independent of a Harbor checkout.
LANGUAGE_BY_REPO = {
    "apache/druid": "java",
    "apache/lucene": "java",
    "google/gson": "java",
    "javaparser/javaparser": "java",
    "projectlombok/lombok": "java",
    "reactivex/rxjava": "java",
    "vuejs/core": "javascript",
    "axios/axios": "javascript",
    "babel/babel": "javascript",
    "facebook/docusaurus": "javascript",
    "immutable-js/immutable-js": "javascript",
    "mrdoob/three.js": "javascript",
    "preactjs/preact": "javascript",
    "caddyserver/caddy": "go",
    "gin-gonic/gin": "go",
    "gohugoio/hugo": "go",
    "hashicorp/terraform": "go",
    "prometheus/prometheus": "go",
    "astral-sh/ruff": "rust",
    "burntsushi/ripgrep": "rust",
    "nushell/nushell": "rust",
    "sharkdp/bat": "rust",
    "tokio-rs/axum": "rust",
    "tokio-rs/tokio": "rust",
    "uutils/coreutils": "rust",
    "jqlang/jq": "c",
    "micropython/micropython": "c",
    "redis/redis": "c",
    "valkey-io/valkey": "c",
    "fmtlib/fmt": "cpp",
    "nlohmann/json": "cpp",
    "briannesbitt/carbon": "php",
    "laravel/framework": "php",
    "php-cs-fixer/php-cs-fixer": "php",
    "phpoffice/phpspreadsheet": "php",
    "faker-ruby/faker": "ruby",
    "fastlane/fastlane": "ruby",
    "fluent/fluentd": "ruby",
    "jekyll/jekyll": "ruby",
    "jordansissel/fpm": "ruby",
    "rubocop/rubocop": "ruby",
}

LANGUAGE_ALLOCATION = {
    "c": 2,
    "cpp": 2,
    "go": 3,
    "java": 3,
    "javascript": 3,
    "php": 2,
    "ruby": 2,
    "rust": 3,
}

# This is an intake exclusion, not a judgment about the upstream task.  The
# Harbor adapter documents a seasonal verifier problem for this instance.
EXCLUDED_INSTANCE_REASONS = {
    "briannesbitt__carbon-3073": "known seasonal verifier issue in local adapter",
}

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CANARY_RE = re.compile(r"^\s*#.*\bcanary\b", re.IGNORECASE)
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+")
BOILERPLATE_RE = re.compile(
    r"(?:please\s+(?:complete|read|follow)|thanks\s+for\s+helping|"
    r"don.t\s+remove\s+me|important\s+notice\s+to\s+read|"
    r"have\s+you\s+read\s+the\s+contributing\s+guidelines|"
    r"would\s+you\s+like\s+to\s+work\s+on\s+a\s+fix|"
    r"before\s+you\s+submit\s+.*\bissue\b|"
    r"^\s*(?:dibs\b|ping\s+@))",
    re.IGNORECASE,
)
EMPTY_RESPONSE_RE = re.compile(r"^\s*_(?:no response|none)\s*_?\s*$", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
BOLD_HEADING_RE = re.compile(r"^\s*\*{1,2}([^*]+)\*{1,2}\s*:?\s*$")
DROP_HEADING_RE = re.compile(
    r"(?:environment|system information|compiler and operating system|"
    r"\bversion(?:\s+info)?\b|\bplatform\b|\bbrowser\b|\bdevice\b|"
    r"\bos\b|additional context|^logs?$|error log|alertmanager version|"
    r"configuration file|library version|contribution checks|how do you run|"
    r"^references?$|screenshots)",
    re.IGNORECASE,
)
ORACLE_LEAK_RE = re.compile(
    r"(?:FAIL_TO_PASS|PASS_TO_PASS|gold\s+patch|test_patch|solution/solve\.sh|"
    r"/logs/artifacts/patch\.diff)",
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def clean_problem_statement(raw: str) -> tuple[str, list[str], list[str]]:
    """Conservatively remove issue-template noise without rewriting content."""

    operations = [
        "normalize_line_endings",
        "remove_ansi_sequences",
        "remove_html_comments",
        "remove_canary_lines",
        "remove_issue_template_checkboxes",
        "remove_submission_boilerplate_lines",
        "remove_environment_and_metadata_sections",
        "collapse_repeated_blank_lines",
    ]
    text = ANSI_RE.sub("", raw.replace("\r\n", "\n").replace("\r", "\n"))
    text = HTML_COMMENT_RE.sub("", text)
    out: list[str] = []
    dropping_section = False
    in_fence = False
    removed_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line.rstrip())
            continue
        if not in_fence:
            heading = HEADING_RE.match(line) or BOLD_HEADING_RE.match(line)
            if heading:
                heading_text = heading.group(1).strip("* `")
                if DROP_HEADING_RE.search(heading_text):
                    dropping_section = True
                    removed_lines.append(line)
                    continue
                dropping_section = False
            if dropping_section:
                removed_lines.append(line)
                continue
            if CHECKBOX_RE.match(line) or CANARY_RE.match(line):
                removed_lines.append(line)
                continue
            if BOILERPLATE_RE.search(stripped) or EMPTY_RESPONSE_RE.match(line):
                removed_lines.append(line)
                continue
        out.append(line.rstrip())

    cleaned = "\n".join(out).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Issue labels are metadata, not part of the requested behavior.
    cleaned = re.sub(r"^(?:\[BUG\]|\[FEATURE\])\s*", "", cleaned, flags=re.I)
    flags: list[str] = []
    if len(cleaned) > MAX_CLEANED_STATEMENT_CHARS:
        flags.append("long_statement")
    if ORACLE_LEAK_RE.search(cleaned):
        flags.append("possible_oracle_leak")
    if re.search(r"(?:please\s+describe|fill\s+in\s+as\s+much|no\s+response)", cleaned, re.I):
        flags.append("template_residue")
    if not cleaned:
        flags.append("empty_after_cleanup")
    return cleaned, operations, flags


def diff_paths(diff: str) -> list[str]:
    paths: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("diff --git "):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        path = parts[3]
        if path.startswith("b/"):
            path = path[2:]
        if path not in paths:
            paths.append(path)
    return paths


def is_new_file(diff: str) -> bool:
    return "new file mode " in diff or "--- /dev/null" in diff


def added_comment(diff: str) -> bool:
    return any(
        re.match(r"^\+\s*(?://|/\*|\*|#\s|--\s)", line)
        for line in diff.splitlines()
    )


def derive_opportunities(row: dict[str, Any], language: str) -> list[str]:
    """Derive coarse curation tags from evaluator-side patch shape.

    The patch itself is never written to a TaskSpec.  These tags are deliberately
    broad and are not claims that the tagged behavior will occur in every run.
    """

    patch = row.get("patch", "") or ""
    test_patch = row.get("test_patch", "") or ""
    paths = diff_paths(patch)
    test_paths = diff_paths(test_patch)
    issue_text = str(row.get("problem_statement", ""))
    combined = (issue_text + "\n" + patch).lower()
    tags: list[str] = []

    def add(tag: str) -> None:
        if tag not in tags:
            tags.append(tag)

    if patch.strip():
        add("behavior_change")
        add("source_edit")
    if test_patch.strip():
        add("test_authoring")
    if len(paths) > 1:
        add("multi_file_change")
    if is_new_file(patch):
        add("new_file")
    if any(re.search(r"(?:^|/)(?:docs?|documentation)(?:/|$)|\.(?:md|rst|adoc)$", p, re.I) for p in paths):
        add("documentation_edit")
    if any(re.search(r"\.(?:ya?ml|json|toml|ini|xml)$", p, re.I) for p in paths):
        add("configuration_edit")
    if re.search(r"(?:api|endpoint|request|response|header|route|public interface)", combined, re.I):
        add("public_api_change")
        add("api_change")
    if re.search(r"(?:json object|schema|kind|apiVersion|resource collection|spec and status)", combined, re.I):
        add("api_object_definition")
    if re.search(r"(?:controller|desired state|observed state|status field)", combined, re.I):
        add("controller_state_update")
    if re.search(r"(?:optional depend|importerror)", combined, re.I):
        add("optional_dependency_import")
    if re.search(r"(?:warning|deprecation)", combined, re.I):
        add("warning_assertion")
    if language == "rust" and re.search(r"\b(?:pub|trait|impl|fn)\b", patch):
        add("rust_api_edit")
    if language == "rust" and re.search(r"\bmatch\b", patch):
        add("rust_match_edit")
    if language == "go" and is_new_file(patch) and any(p.endswith(".go") for p in paths):
        add("go_file_creation")
    if re.search(r"generated|codegen|boilerplate", combined, re.I):
        add("generated_file_edit")
    if added_comment(patch):
        add("code_comment_edit")
    # A changed test gives a plausible test-authoring opportunity, while the
    # actual event remains a run-time observation.
    if test_paths and re.search(r"(?:bug|feature|fix|support|implement)", issue_text, re.I):
        add("behavior_test_change")
    return tags


def materialized_task_exists(harbor_root: Path, instance_id: str) -> bool:
    task_dir = harbor_root / instance_id
    return all((task_dir / name).is_file() for name in ("task.toml", "instruction.md", "tests/test.sh"))


def eligible_rows(rows: Iterable[dict[str, Any]], harbor_root: Path) -> tuple[list[dict[str, Any]], Counter[str], dict[str, str]]:
    eligible: list[dict[str, Any]] = []
    excluded: Counter[str] = Counter()
    excluded_ids: dict[str, str] = {}
    for row in rows:
        instance_id = str(row.get("instance_id", ""))
        reason: str | None = None
        if not LANGUAGE_BY_REPO.get(str(row.get("repo", ""))):
            reason = "unknown_language"
        elif not str(row.get("problem_statement", "")).strip():
            reason = "empty_problem_statement"
        elif not str(row.get("patch", "")).strip() or not str(row.get("test_patch", "")).strip():
            reason = "missing_oracle_patch"
        elif not materialized_task_exists(harbor_root, instance_id):
            reason = "missing_harbor_materialization"
        elif instance_id in EXCLUDED_INSTANCE_REASONS:
            reason = "known_upstream_verifier_issue"
        else:
            cleaned, _, flags = clean_problem_statement(str(row["problem_statement"]))
            if "empty_after_cleanup" in flags:
                reason = "empty_after_cleanup"
            elif "possible_oracle_leak" in flags:
                reason = "possible_oracle_leak"
            elif "long_statement" in flags:
                reason = "long_statement"
            elif "template_residue" in flags:
                reason = "template_residue"
        if reason:
            excluded[reason] += 1
            excluded_ids[instance_id] = EXCLUDED_INSTANCE_REASONS.get(instance_id, reason)
        else:
            eligible.append(row)
    eligible.sort(key=lambda item: str(item["instance_id"]))
    return eligible, excluded, excluded_ids


def choose_panel(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = {
        language: [row for row in rows if LANGUAGE_BY_REPO[row["repo"]] == language]
        for language in LANGUAGE_ALLOCATION
    }
    languages = list(LANGUAGE_ALLOCATION)
    for offset, language in enumerate(languages):
        random.Random(SEED + offset * 997).shuffle(groups[language])

    selected: list[dict[str, Any]] = []
    repo_counts: Counter[str] = Counter()
    for language in languages:
        needed = LANGUAGE_ALLOCATION[language]
        for row in groups[language]:
            repo = str(row["repo"])
            if repo_counts[repo] != 0:
                continue
            selected.append(row)
            repo_counts[repo] += 1
            if sum(LANGUAGE_BY_REPO[item["repo"]] == language for item in selected) == needed:
                break
        actual = sum(LANGUAGE_BY_REPO[item["repo"]] == language for item in selected)
        if actual != needed:
            raise RuntimeError(f"Could not allocate {needed} tasks for {language}; got {actual}")

    reserve: list[dict[str, Any]] = []
    for language in languages:
        for row in groups[language]:
            repo = str(row["repo"])
            if row in selected or repo_counts[repo] >= 2:
                continue
            reserve.append(row)
            repo_counts[repo] += 1
            break
    return selected, reserve


def yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(
        value,
        allow_unicode=True,
        sort_keys=False,
        width=100,
        default_flow_style=False,
    ).encode("utf-8")


def make_task_spec(
    row: dict[str, Any],
    *,
    parquet_sha256: str,
    harbor_adapter_commit: str,
) -> dict[str, Any]:
    instance_id = str(row["instance_id"])
    repo = str(row["repo"])
    language = LANGUAGE_BY_REPO[repo]
    raw_text = str(row["problem_statement"])
    cleaned, operations, quality_flags = clean_problem_statement(raw_text)
    row_hash = sha256_bytes(canonical_json(row))
    return {
        "format": "hif.task_spec",
        "format_version": FORMAT_VERSION,
        "status": "candidate",
        "created_at": COLLECTION_DATE,
        "task_id": f"swebench-multilingual/{instance_id}",
        "source": {
            "dataset": DATASET_NAME,
            "config": DATASET_CONFIG,
            "split": DATASET_SPLIT,
            "revision": DATASET_REVISION,
            "instance_id": instance_id,
            "parquet_sha256": parquet_sha256,
            "row_sha256": row_hash,
            "retrieved_at": COLLECTION_DATE,
        },
        "repository": {
            "slug": repo,
            "base_commit": str(row["base_commit"]),
            "upstream_version": str(row.get("version", "")),
            "language": language,
            "difficulty": "hard",
            "difficulty_derivation": "harbor_adapter_default",
        },
        "content": {
            "problem_statement": cleaned,
            "hints_policy": "omitted",
            "normalization": {
                "operations": operations,
                "raw_text_sha256": sha256_text(raw_text.replace("\r\n", "\n").replace("\r", "\n")),
                "cleaned_text_sha256": sha256_text(cleaned),
            },
        },
        "curation": {
            "status": "eligible_candidate",
            "offers_opportunity": derive_opportunities(row, language),
            "opportunity_derivation": {
                "method": "evaluator_patch_shape_v1",
                "evaluator_only": True,
                "note": "Tags are matching hints, not assertions about a particular run.",
            },
            "screening": {
                "problem_statement_present": True,
                "base_commit_present": True,
                "language_known": True,
                "harbor_materialization_present": True,
                "hidden_oracle_model_visible": False,
                "quality_flags": quality_flags,
            },
        },
        "fixture_ref": {
            "provider": "swebench_multilingual",
            "cache_key": f"swebench-multilingual/{DATASET_REVISION}/{instance_id}",
            "visibility": "evaluator_only",
        },
        "evaluator_ref": {
            "visibility": "evaluator_only",
            "provider": "swebench_multilingual",
            "source_row_sha256": row_hash,
            "oracle_fields": ["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"],
            "materializer": {
                "repository": "harbor",
                "adapter": "adapters/swebench_multilingual",
                "adapter_commit": harbor_adapter_commit,
                "generated_task_dir_pattern": "<external-harbor-root>/<instance_id>",
            },
        },
        "visibility": {
            "model_visible": ["content.problem_statement"],
            "compiler_metadata": ["source", "repository", "curation.offers_opportunity"],
            "evaluator_only": ["fixture_ref", "evaluator_ref"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True, help="Local parquet snapshot of the test split")
    parser.add_argument("--harbor-root", type=Path, required=True, help="External generated Harbor task root")
    parser.add_argument("--output-dir", type=Path, required=True, help="Repository benchmark/tasks directory")
    parser.add_argument(
        "--harbor-adapter-commit",
        default="c1769aaba90d88ac1bd19206c1fc8485a420b980",
        help="Immutable Harbor commit used for task materialization metadata",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace existing generated specs/index")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.parquet.is_file():
        raise SystemExit(f"Parquet snapshot not found: {args.parquet}")
    if not args.harbor_root.is_dir():
        raise SystemExit(f"Harbor task root not found: {args.harbor_root}")

    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - environment guidance
        raise SystemExit("The collection tool requires the 'datasets' package") from exc

    dataset = load_dataset(
        "parquet",
        data_files={DATASET_SPLIT: str(args.parquet)},
        split=DATASET_SPLIT,
    )
    rows = [dict(row) for row in dataset]
    parquet_sha256 = sha256_bytes(args.parquet.read_bytes())
    eligible, excluded, excluded_ids = eligible_rows(rows, args.harbor_root)
    selected, reserve = choose_panel(eligible)
    selected_ids = [str(row["instance_id"]) for row in selected]
    reserve_ids = [str(row["instance_id"]) for row in reserve]

    spec_dir = args.output_dir / "specs" / "swebench-multilingual"
    index_dir = args.output_dir / "indexes"
    if not args.overwrite and (spec_dir.exists() or index_dir.joinpath("swebench-multilingual-pilot-20.yaml").exists()):
        raise SystemExit("Generated task records already exist; use --overwrite explicitly")
    if args.overwrite and spec_dir.exists():
        # The directory is generated output; clear stale specs so an index can
        # never coexist with records from an earlier selection.
        for stale_spec in spec_dir.glob("*.yaml"):
            stale_spec.unlink()
    spec_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    spec_hashes: dict[str, str] = {}
    spec_records: dict[str, dict[str, Any]] = {}
    for row in selected:
        spec = make_task_spec(row, parquet_sha256=parquet_sha256, harbor_adapter_commit=args.harbor_adapter_commit)
        path = spec_dir / f"{row['instance_id']}.yaml"
        payload = yaml_bytes(spec)
        path.write_bytes(payload)
        spec_hashes[str(row["instance_id"])] = sha256_bytes(payload)
        spec_records[str(row["instance_id"])] = spec

    implementation_hash = sha256_bytes(Path(__file__).read_bytes())
    language_counts = Counter(LANGUAGE_BY_REPO[row["repo"]] for row in selected)
    repo_counts = Counter(str(row["repo"]) for row in selected)
    index = {
        "format": "hif.task_index",
        "format_version": FORMAT_VERSION,
        "status": "candidate_panel",
        "created_at": COLLECTION_DATE,
        "dataset": {
            "name": DATASET_NAME,
            "config": DATASET_CONFIG,
            "split": DATASET_SPLIT,
            "revision": DATASET_REVISION,
            "parquet_sha256": parquet_sha256,
            "row_count": len(rows),
        },
        "population": {
            "size_before_filters": len(rows),
            "size_after_filters": len(eligible),
            "excluded_counts": dict(sorted(excluded.items())),
            "excluded_ids": excluded_ids,
            "filters": [
                "known_repository_language",
                "nonempty_problem_statement",
                "nonempty_patch_and_test_patch_for_evaluator_reference",
                "harbor_task.toml_instruction_and_test_materialization_present",
                "exclude_known_local_verifier_issue",
                "reject_possible_oracle_leak_after_cleanup",
                f"cleaned_problem_statement_at_most_{MAX_CLEANED_STATEMENT_CHARS}_characters",
                "reject_residual_issue_template_boilerplate",
            ],
        },
        "sampling": {
            "method": "language_stratified_random_without_replacement",
            "seed": SEED,
            "language_allocation": LANGUAGE_ALLOCATION,
            "selected_repo_cap": 1,
            "reserve_per_language": 1,
            "reserve_repo_cap": 2,
            "algorithm": "sort_by_instance_id_then_shuffle_each_language_with_seed_plus_offset",
            "implementation": {
                "path": "benchmark/tasks/generators/collect_swebench_multilingual.py",
                "version": "0",
                "sha256": implementation_hash,
            },
        },
        "selected_ids": selected_ids,
        "reserve_ids": reserve_ids,
        "selection_stats": {
            "language_counts": dict(sorted(language_counts.items())),
            "repository_counts": dict(sorted(repo_counts.items())),
        },
        "task_specs": [
            {
                "task_id": f"swebench-multilingual/{instance_id}",
                "path": f"benchmark/tasks/specs/swebench-multilingual/{instance_id}.yaml",
                "sha256": spec_hashes[instance_id],
                "language": LANGUAGE_BY_REPO[spec_records[instance_id]["repository"]["slug"]],
                "repository": spec_records[instance_id]["repository"]["slug"],
            }
            for instance_id in selected_ids
        ],
        "external_inputs": {
            "task_cache": "<HIF_TASK_CACHE>/swebench-multilingual/<revision>/<instance-id>",
            "harbor_materialization": "<external-harbor-root>/<instance-id>",
            "model_visible_projection": ["content.problem_statement"],
        },
        "notes": [
            "This is a fixed candidate panel, not a released benchmark split.",
            "Reserve IDs are not represented by TaskSpecs until substituted before a release freeze.",
            "Patches, tests, full repositories, and Harbor task directories remain external.",
        ],
    }
    index_path = index_dir / "swebench-multilingual-pilot-20.yaml"
    index_path.write_bytes(yaml_bytes(index))
    print(f"selected={len(selected)} reserve={len(reserve)} eligible={len(eligible)} total={len(rows)}")
    print(f"index={index_path}")


if __name__ == "__main__":
    main()
