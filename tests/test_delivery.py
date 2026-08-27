from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from compilers.harbor.compiler import HarborPackCompiler
from hif.delivery import DeliveryError, build_delivery_manifest

ROOT = Path(__file__).resolve().parents[1]
ITEM = ROOT / "examples/smoke/item-pair.yaml"
RULES = ROOT / "benchmark/rules/canonical/phase0-canonical.yaml"
TASK_SPEC = ROOT / "examples/smoke/task-spec.yaml"
TASK = ROOT / "examples/smoke/task"


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
    item["intervention"]["rule_bindings"][0]["target_surface"] = "system_prompt"
    item_path = tmp_path / "unsupported.yaml"
    item_path.write_text(yaml.safe_dump(item, sort_keys=False))

    with pytest.raises(DeliveryError, match="unsupported first-stage surface"):
        build_delivery_manifest(
            item_path=item_path,
            rule_library_path=RULES,
            task_spec_path=TASK_SPEC,
            output_dir=tmp_path / "delivery",
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
