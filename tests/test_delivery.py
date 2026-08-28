from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from compilers.harbor.compiler import HarborPackCompiler
from harnesses.stepcli.adapter import StepCliDeliveryAdapter
from hif.delivery import DeliveryError, build_delivery_manifest

ROOT = Path(__file__).resolve().parents[1]
ITEM = ROOT / "examples/smoke/item-pair.yaml"
RULES = ROOT / "benchmark/rules/canonical/phase0-canonical.yaml"
TASK_SPEC = ROOT / "examples/smoke/task-spec.yaml"
TASK = ROOT / "examples/smoke/task"
TOOL_ITEM = ROOT / "examples/smoke/tool-surface-item-pair.yaml"


def test_stepcli_manifest_keeps_user_and_project_bindings_separate(tmp_path: Path):
    manifest = build_delivery_manifest(
        item_path=ITEM,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        output_dir=tmp_path / "delivery",
        variant="intervention",
    )

    assert [entry["intended_surface"] for entry in manifest["deliveries"]] == [
        "user_message",
        "project_file",
    ]
    assert manifest["deliveries"][0]["transport"] == "harbor.extra_instruction_paths"
    assert manifest["deliveries"][1]["transport"].endswith("upload_files")
    assert len(manifest["surfaces"]["user_message"]["fragments"]) == 1
    assert len(manifest["surfaces"]["project_file"]["files"]) == 1
    assert (tmp_path / "delivery/user_messages/rb-user-test.md").is_file()
    assert (tmp_path / "delivery/project_files/rb-project-comments.md").is_file()
    assert json.loads((tmp_path / "delivery/manifest.json").read_text()) == manifest


def test_baseline_has_no_surface_payloads(tmp_path: Path):
    manifest = build_delivery_manifest(
        item_path=ITEM,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        output_dir=tmp_path / "delivery",
        variant="baseline",
    )
    assert manifest["deliveries"] == []
    assert manifest["surfaces"]["user_message"]["fragments"] == []
    assert manifest["surfaces"]["project_file"]["files"] == []


def test_user_fragments_follow_explicit_delivery_order(tmp_path: Path):
    item = yaml.safe_load(ITEM.read_text())
    bindings = item["intervention"]["rule_bindings"]
    bindings[0]["target_surface"] = "user_message"
    bindings[0]["delivery_order"] = 20
    bindings[1]["target_surface"] = "user_message"
    bindings[1]["delivery_order"] = 10
    item_path = tmp_path / "ordered.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    manifest = build_delivery_manifest(
        item_path=item_path,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        output_dir=tmp_path / "delivery",
    )

    fragments = manifest["surfaces"]["user_message"]["fragments"]
    assert [fragment["delivery_order"] for fragment in fragments] == [10, 20]
    assert [fragment["binding_id"] for fragment in fragments] == [
        "rb-project-comments",
        "rb-user-test",
    ]
    assert [entry["binding_id"] for entry in manifest["deliveries"]] == [
        "rb-project-comments",
        "rb-user-test",
    ]


def test_duplicate_delivery_order_is_rejected(tmp_path: Path):
    item = yaml.safe_load(ITEM.read_text())
    item["intervention"]["rule_bindings"][1]["delivery_order"] = 1
    item_path = tmp_path / "duplicate-order.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    with pytest.raises(DeliveryError, match="reuses delivery_order"):
        build_delivery_manifest(
            item_path=item_path,
            rule_library_path=RULES,
            task_spec_path=TASK_SPEC,
            output_dir=tmp_path / "delivery",
        )


def test_unsupported_surface_is_explicitly_rejected(tmp_path: Path):
    item = yaml.safe_load(ITEM.read_text())
    item["intervention"]["rule_bindings"][0]["target_surface"] = "managed_instruction"
    item_path = tmp_path / "unsupported.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    with pytest.raises(DeliveryError, match="unsupported first-stage surface"):
        build_delivery_manifest(
            item_path=item_path,
            rule_library_path=RULES,
            task_spec_path=TASK_SPEC,
            output_dir=tmp_path / "delivery",
        )


def test_system_prompt_fragments_are_materialized_and_ordered(tmp_path: Path):
    item = yaml.safe_load(ITEM.read_text())
    bindings = item["intervention"]["rule_bindings"]
    bindings[0]["target_surface"] = "system_prompt"
    bindings[0]["delivery_order"] = 20
    bindings[1]["target_surface"] = "system_prompt"
    bindings[1]["delivery_order"] = 10
    item_path = tmp_path / "system-item.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    manifest = build_delivery_manifest(
        item_path=item_path,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        output_dir=tmp_path / "delivery",
    )

    fragments = manifest["surfaces"]["system_prompt"]["fragments"]
    assert [entry["binding_id"] for entry in fragments] == [
        "rb-project-comments",
        "rb-user-test",
    ]
    assert [entry["delivery_order"] for entry in fragments] == [10, 20]
    assert [entry["intended_surface"] for entry in manifest["deliveries"]] == [
        "system_prompt",
        "system_prompt",
    ]
    assert manifest["surfaces"]["system_prompt"]["merge_strategy"] == (
        "ordered_join_double_newline"
    )
    first = (tmp_path / "delivery/system_prompts/rb-project-comments.md").read_text()
    second = (tmp_path / "delivery/system_prompts/rb-user-test.md").read_text()
    merged = f"{first.strip()}\n\n{second.strip()}"
    surface = manifest["surfaces"]["system_prompt"]
    assert surface["merged_content_sha256"] == hashlib.sha256(
        merged.encode("utf-8")
    ).hexdigest()
    assert surface["merged_content_bytes"] == len(merged.encode("utf-8"))


def test_harbor_pack_forwards_merged_system_prompt_and_checks_conflicts(
    tmp_path: Path,
):
    item = yaml.safe_load(ITEM.read_text())
    item["intervention"]["rule_bindings"][0]["target_surface"] = "system_prompt"
    item_path = tmp_path / "system-item.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    pack = HarborPackCompiler().compile(
        item_path=item_path,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        task_dir=TASK,
        output_root=tmp_path / "pack",
        model_name="openai/test-model",
    )
    launch = yaml.safe_load((pack / "launch.yaml").read_text())
    kwargs = launch["agents"][0]["kwargs"]
    expected = (pack / "delivery/system_prompts/rb-user-test.md").read_text().strip()
    assert kwargs["stepcli_instruction_prompt"] == expected
    assert launch["extra_instruction_paths"] == []
    manifest = json.loads((pack / "delivery/manifest.json").read_text())
    assert manifest["surfaces"]["system_prompt"]["fragments"]

    with pytest.raises(ValueError, match="stepcli_instruction_prompt disagrees"):
        HarborPackCompiler().compile(
            item_path=item_path,
            rule_library_path=RULES,
            task_spec_path=TASK_SPEC,
            task_dir=TASK,
            output_root=tmp_path / "conflict-pack",
            model_name="openai/test-model",
            agent_kwargs={"stepcli_instruction_prompt": "different"},
        )


def test_harbor_pack_projects_clean_task_text_and_upload_hook(tmp_path: Path):
    pack = HarborPackCompiler().compile(
        item_path=ITEM,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        task_dir=TASK,
        output_root=tmp_path,
        model_name="openai/test-model",
    )

    assert pack == tmp_path / "smoke-user-project-v1--intervention"
    generated_task = pack / "dataset/user-project"
    statement = yaml.safe_load(TASK_SPEC.read_text())["content"]["problem_statement"].rstrip()
    assert (generated_task / "instruction.md").read_text().rstrip() == statement
    project_path = generated_task / "environment/.claude/rules/hif-rb-project-comments.md"
    assert project_path.read_text().strip()

    launch = yaml.safe_load((pack / "launch.yaml").read_text())
    assert launch["job_name"] == "smoke-user-project-v1--intervention"
    assert launch["tasks"] == [{"path": str(generated_task.resolve())}]
    assert launch["extra_instruction_paths"] == [
        str((pack / "delivery/user_messages/rb-user-test.md").resolve())
    ]
    hook = launch["environment"]["setup_hooks"][0]
    assert hook["name"] == "upload_files"
    assert hook["stages"] == ["agent"]
    assert hook["kwargs"]["files"] == [
        {
            "source": ".claude/rules/hif-rb-project-comments.md",
            "target": "/testbed/.claude/rules/hif-rb-project-comments.md",
        }
    ]

    metadata = json.loads((pack / "pack.json").read_text())
    assert metadata["paths"]["delivery_manifest"] == "delivery/manifest.json"
    assert metadata["compiler_version"] == "0.2.0"


def test_stepcli_adapter_projects_tool_set_and_description_binding(tmp_path: Path):
    manifest = StepCliDeliveryAdapter().compile(
        item_path=TOOL_ITEM,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        output_dir=tmp_path / "delivery",
        variant="intervention",
    )

    rules = yaml.safe_load(RULES.read_text())["records"]
    statement = next(
        record["statement"]
        for record in rules
        if record["id"] == "rule-canon-p0-038"
    ).strip()
    assert manifest["item"]["tool_set_ref"] == "dsh_minimal"
    assert manifest["tool_set"] == {
        "requested_ref": "dsh_minimal",
        "status": "planned",
        "adapter_projection": "harnesses/stepcli/adapter.py",
        "active_surface": "dsh_minimal",
        "resolved_tool_refs": {
            "editor": "str_replace_editor",
            "shell": "bash",
        },
        "resolved_tool_names": ["bash", "str_replace_editor"],
        "description_override_tool_names": ["bash"],
    }
    assert manifest["harness_config"]["stepcli"]["extension_surface"] == {
        "active": "dsh_minimal",
        "surfaces": {
            "dsh_minimal": {
                "tools": {
                    "descriptionOverrides": {
                        "bash": {"mode": "append", "text": statement}
                    }
                }
            }
        },
    }
    tool_binding = next(
        entry
        for entry in manifest["deliveries"]
        if entry["binding_id"] == "rb-tool-description"
    )
    assert tool_binding["resolved_tool_names"] == ["bash"]
    assert tool_binding["status"] == "planned"
    assert manifest["provenance"]["adapter_version"] == "0.2.0"


def test_harbor_pack_forwards_stepcli_surface_config_without_flattening(tmp_path: Path):
    pack = HarborPackCompiler().compile(
        item_path=TOOL_ITEM,
        rule_library_path=RULES,
        task_spec_path=TASK_SPEC,
        task_dir=TASK,
        output_root=tmp_path,
        model_name="openai/test-model",
    )

    launch = yaml.safe_load((pack / "launch.yaml").read_text())
    kwargs = launch["agents"][0]["kwargs"]
    assert kwargs["stepcli_extension_surface"]["active"] == "dsh_minimal"
    assert "descriptionOverrides" in kwargs["stepcli_extension_surface"]["surfaces"][
        "dsh_minimal"
    ]["tools"]
    manifest = json.loads((pack / "delivery/manifest.json").read_text())
    assert [entry["intended_surface"] for entry in manifest["deliveries"]] == [
        "user_message",
        "project_file",
        "tool_description",
    ]
