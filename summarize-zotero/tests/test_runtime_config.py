import argparse
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "summarize_zotero.py"
SPEC = importlib.util.spec_from_file_location("summarize_zotero", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RuntimeConfigTests(unittest.TestCase):
    def test_builds_config_from_resolved_project_values(self):
        args = argparse.Namespace(
            collection_key="5UKV2FYM",
            collection_name=None,
            vault_path="/tmp/Obsidian Vault",
            output_folder="library/zotero-previews",
            filename_pattern="@{citekey}",
        )

        config = MODULE.runtime_config_from_args(args)

        self.assertEqual(config["zotero"]["collection_key"], "5UKV2FYM")
        self.assertEqual(config["obsidian"]["vault_path"], "/tmp/Obsidian Vault")
        self.assertEqual(config["obsidian"]["output_folder"], "library/zotero-previews")
        self.assertEqual(config["obsidian"]["filename_pattern"], "@{citekey}")

    def test_reports_only_missing_required_values(self):
        args = argparse.Namespace(
            collection_key=None,
            collection_name=None,
            vault_path="/tmp/Obsidian Vault",
            output_folder=None,
            filename_pattern="@{citekey}",
        )

        with self.assertRaisesRegex(
            ValueError,
            "collection_key or collection_name, output_folder",
        ):
            MODULE.runtime_config_from_args(args)


if __name__ == "__main__":
    unittest.main()
