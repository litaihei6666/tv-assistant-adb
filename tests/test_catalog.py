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
        self.assertEqual((ROOT / "index.html").read_text(encoding="utf-8"), build.render(self.entries))
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

if __name__ == "__main__": unittest.main()
