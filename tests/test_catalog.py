import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build", ROOT / "scripts/build.py")
build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)

class CatalogTests(unittest.TestCase):
    def setUp(self): self.entries = build.load_records()
    def test_source_catalog_and_generated_index_are_consistent(self):
        self.assertGreaterEqual(len(self.entries), 1)
        self.assertEqual((ROOT / "index.html").read_text(encoding="utf-8"), build.render(self.entries, build.load_research()))
    def test_unknown_factory_paths_do_not_contain_steps(self):
        for e in self.entries:
            if e["status"] == "unresolved": self.assertEqual(e["steps"], [])
            for step in e["steps"]:
                self.assertNotIn("adb shell", step.lower())
                self.assertNotIn("恢复出厂", step)
                self.assertNotIn("工厂菜单密码", step)
    def test_ht2_source_is_not_upgraded_and_wireless_is_unknown(self):
        e = next(x for x in self.entries if x["id"] == "hinlink-ht2")
        self.assertEqual(e["evidence"], "community"); self.assertEqual(e["transport"], "usb")
        self.assertTrue(any("无线连接未知" in x for x in e["limitations"]))
    def test_untrusted_text_is_escaped_in_html(self):
        e = copy.deepcopy(self.entries[0]); e["title"] = "<script>alert(1)</script>"
        content = build.render([e]); self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<script>alert(1)</script>", content)
    def test_exact_model_and_unknown_firmware_are_recorded(self):
        e = next(x for x in self.entries if x["id"] == "tcl-65v6d")
        self.assertEqual(e["models"], ["65V6D"]); self.assertIn("固件未知", e["scope"])
        self.assertEqual(e["evidence"], "firsthand_report")
    def test_context_is_visible_searchable_and_escaped(self):
        e = copy.deepcopy(self.entries[0])
        e["context"] = {"system": "Android TV 14", "firmware": "<script>alert(1)</script>", "region": "未知"}
        content = build.render([e])
        self.assertIn("系统：Android TV 14", content)
        self.assertIn("地区：未知", content)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)
        self.assertNotIn("<script>alert(1)</script>", content)
    def test_invalid_context_cannot_silently_authorize_more_fields(self):
        for context in ({"system": "unknown"}, {"system": "unknown", "firmware": "unknown", "region": "unknown", "verified": True}):
            e = copy.deepcopy(self.entries[0]); e["context"] = context
            with patch.object(Path, "read_text", return_value=json.dumps({"schema_version": 1, "entries": [e]})):
                with self.assertRaises(ValueError): build.load_records()
    def test_research_cannot_gain_steps_or_verified_status(self):
        commit = "ab7a89e7"
        row = {"id": "test-model", "brand": "test", "title": "Test model", "system": "unknown", "source_url": f"https://github.com/Gathin23/cleanyourtv/blob/{commit}/examples/test-model/debloat.txt", "metadata_sha256": "a"*64, "status": "unreviewed"}
        for changes in ({"status": "verified"}, {"steps": ["an instruction"]}, {"source_url": "https://example.org/"}):
            invalid = {**row, **changes}
            raw = {"schema_version": 1, "source": {"repository": "Gathin23/cleanyourtv", "commit": commit, "index_url": f"https://github.com/Gathin23/cleanyourtv/blob/{commit}/examples/README.md", "index_sha256": "a"*64}, "records": [invalid]}
            with patch.object(Path, "exists", return_value=True), patch.object(Path, "read_text", return_value=json.dumps(raw)):
                with self.assertRaises(ValueError): build.load_research()
    def test_research_brand_aliases_are_searchable_without_adding_steps(self):
        row = {"brand": "Haier", "title": "H32S80EFX", "system": "Google TV 14", "source_url": "https://example.org/model"}
        content = build.render([], [row])
        self.assertIn('data-search="haier 海尔 h32s80efx google tv 14"', content)
        self.assertIn("未审查 · 无操作步骤", content)
        self.assertNotIn("<ol>", content)
        self.assertIn("Sony", build.brand_terms(["索尼"], build.load_aliases()))
    def test_research_metadata_is_escaped(self):
        row = {"brand": "<img src=x onerror=alert(1)>", "title": "<script>alert(1)</script>", "system": "unknown", "source_url": "https://example.org/model"}
        content = build.render([], [row])
        self.assertNotIn("<img src=x", content)
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", content)

if __name__ == "__main__": unittest.main()
