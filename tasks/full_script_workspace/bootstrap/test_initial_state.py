import os
import shutil
import pytest

SCRIPTS_DIR = "/home/user/windmill-project/f/scripts"
FLOWS_DIR = "/home/user/windmill-project/f/flows"


def test_wmill_binary_available():
    assert shutil.which("wmill") is not None, "wmill binary not found in PATH."


def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_scripts_directory_exists():
    assert os.path.isdir(SCRIPTS_DIR)


for fname in ["fetch_users.ts", "enrich_users.ts", "export_csv.ts"]:
    def _make_test(f):
        def test_fn():
            assert not os.path.exists(os.path.join(SCRIPTS_DIR, f)), \
                f"{f} already exists — agent must create it."
        test_fn.__name__ = f"test_{f.replace('.', '_')}_does_not_exist"
        return test_fn
    globals()[f"test_{fname.replace('.','_')}_does_not_exist"] = _make_test(fname)


def test_flow_yaml_does_not_exist_yet():
    assert not os.path.exists(os.path.join(FLOWS_DIR, "user_export_pipeline.yaml")), \
        "user_export_pipeline.yaml already exists — agent must create it."
