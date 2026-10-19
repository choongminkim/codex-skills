import argparse
import importlib.util
import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
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


class SourceRetrievalTests(unittest.TestCase):
    def args(self, **kwargs):
        values = dict(collection_key="COLLECTION", collection_name=None,
                      vault_path=None, output_folder=None, filename_pattern=None,
                      source_only=True, include_fulltext=True, out=None)
        values.update(kwargs)
        return argparse.Namespace(**values)

    def test_source_only_needs_no_save_settings(self):
        config = MODULE.runtime_config_from_args(self.args())
        self.assertTrue(config["source_only"])
        self.assertEqual(config["obsidian"], {})

    def test_source_only_still_needs_collection(self):
        with self.assertRaisesRegex(ValueError, "Missing required values: collection_key or collection_name$"):
            MODULE.runtime_config_from_args(self.args(collection_key=None))

    def test_destination_mode_still_requires_all_save_settings(self):
        with self.assertRaisesRegex(ValueError, "vault_path, output_folder, filename_pattern"):
            MODULE.runtime_config_from_args(self.args(source_only=False))

    def test_source_only_exports_fulltext_without_note_paths(self):
        rows = [{"key": "ITEM1234", "data": {"title": "A paper"}}]
        fulltext = [{"content": "Paper body", "indexed_pages": 2, "total_pages": 2}]
        output = io.StringIO()
        with patch.object(MODULE, "all_pages", return_value=rows), \
             patch.object(MODULE, "pdf_fulltexts", return_value=fulltext) as fetch, \
             redirect_stdout(output):
            MODULE.cmd_export_items(self.args())
        payload = json.loads(output.getvalue())
        self.assertIsNone(payload["output_dir"])
        self.assertIsNone(payload["items"][0]["note_filename"])
        self.assertEqual(payload["items"][0]["pdf_fulltexts"], fulltext)
        fetch.assert_called_once_with("ITEM1234")

    def test_destination_export_flags_duplicate_names(self):
        rows = [dict(key=key, bibtex="@article{SameKey, title={Paper}}",
                     data={"title": "Paper"}) for key in ("ITEM0001", "ITEM0002")]
        output = io.StringIO()
        args = self.args(source_only=False, vault_path="/tmp/Vault",
                         output_folder="notes", filename_pattern="@{citekey}",
                         include_fulltext=False)
        with patch.object(MODULE, "all_pages", return_value=rows), \
             patch.object(MODULE, "pdf_fulltexts") as fetch, redirect_stdout(output):
            MODULE.cmd_export_items(args)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["output_dir"], "/tmp/Vault/notes")
        self.assertEqual(payload["count"], 2)
        for item in payload["items"]:
            self.assertIsNone(item["note_filename"])
            self.assertIn("collision", item["filename_error"])
        fetch.assert_not_called()


class CitationIdentityTests(unittest.TestCase):
    def item(self, key="ITEM1234", bibtex=None):
        item = {"key": key, "data": {"title": "Paper", "date": "2026",
                "creators": [{"lastName": "Kim"}]}}
        if bibtex is not None:
            item["bibtex"] = bibtex
        return item

    def test_missing_key_is_not_fabricated_from_author_and_year(self):
        row = MODULE.summarize_item(self.item(), "@{citekey}")
        self.assertEqual(row["citekey"], "")
        self.assertEqual(row["citekey_source"], "missing")
        self.assertIsNone(row["note_filename"])
        self.assertIn("Missing citation key", row["filename_error"])

    def test_exported_key_preserves_existing_note_naming(self):
        row = MODULE.summarize_item(self.item(bibtex="@article{Kim2026Sepsis,}"), "@{citekey}")
        self.assertEqual(row["citekey"], "Kim2026Sepsis")
        self.assertEqual(row["citekey_source"], "bibtex")
        self.assertEqual(row["note_filename"], "@Kim2026Sepsis.md")
        self.assertIsNone(row["filename_error"])

    def test_explicit_item_key_pattern_does_not_invent_citation_key(self):
        row = MODULE.summarize_item(self.item(), "{zotero_key}")
        self.assertEqual(row["note_filename"], "ITEM1234.md")
        self.assertEqual(row["citekey"], "")
        self.assertIsNone(row["filename_error"])

    def test_missing_item_key_blocks_item_key_filename(self):
        row = MODULE.summarize_item(self.item(key=""), "{zotero_key}")
        self.assertIsNone(row["note_filename"])
        self.assertIn("Missing Zotero item key", row["filename_error"])

    def test_collisions_after_filename_sanitization_block_all_affected_items(self):
        rows = [MODULE.summarize_item(self.item(key=key, bibtex=f"@article{{{cite},}}"), "@{citekey}")
                for key, cite in [("ITEM0001", "A:B"), ("ITEM0002", "a-b"), ("ITEM0003", "Unique")]]
        MODULE.flag_filename_collisions(rows)
        self.assertEqual([r["note_filename"] for r in rows], [None, None, "@Unique.md"])
        self.assertTrue(all(r["filename_error"] for r in rows[:2]))
        self.assertIsNone(rows[2]["filename_error"])


if __name__ == "__main__":
    unittest.main()
