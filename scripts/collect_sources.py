"""Collect public, pinned model metadata for review; never generate instructions."""
import concurrent.futures
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "ab7a89e7"
BASE = f"https://raw.githubusercontent.com/Gathin23/cleanyourtv/{COMMIT}/"
CACHE = ROOT / ".work" / "sources" / COMMIT


def fetch(relative):
    if not re.fullmatch(r"examples/(?:README\.md|[a-z0-9-]+/(?:tv\.json|debloat\.txt))", relative):
        raise ValueError("Only pinned model documents may be fetched")
    path = CACHE / relative
    if path.exists():
        return path.read_bytes()
    with urllib.request.urlopen(urllib.request.Request(BASE + relative, headers={"User-Agent": "tv-adb-guide-source-review"}), timeout=15) as response:
        raw = response.read(300_001)
    if len(raw) > 300_000:
        raise ValueError("Model document exceeds size limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)
    return raw


def collect(folder):
    try:
        raw = fetch(f"examples/{folder}/tv.json")
        data = json.loads(raw)
        if not all(isinstance(data.get(k), str) and data[k].strip() for k in ("tv", "os", "brand")):
            raise ValueError("Missing model metadata")
        # Full notes are cached privately for review, never interpreted as an instruction.
        fetch(f"examples/{folder}/debloat.txt")
        return {"id": folder, "brand": data["brand"], "title": data["tv"], "system": data["os"],
                "source_url": f"https://github.com/Gathin23/cleanyourtv/blob/{COMMIT}/examples/{folder}/debloat.txt",
                "metadata_sha256": hashlib.sha256(raw).hexdigest(), "status": "unreviewed"}
    except Exception as error:
        return {"id": folder, "error": type(error).__name__}


def main():
    raw = fetch("examples/README.md")
    folders = sorted(set(re.findall(r"^\| `([a-z0-9-]+)/` \|", raw.decode("utf-8"), re.M)))
    if not folders:
        raise SystemExit("No model folders; refusing to replace the existing index")
    records, failures = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for i, result in enumerate(pool.map(collect, folders), 1):
            (failures if "error" in result else records).append(result)
            if i % 25 == 0:
                print(f"Fetched source availability {i}/{len(folders)}", flush=True)
    output = {"schema_version": 1, "source": {"repository": "Gathin23/cleanyourtv", "commit": COMMIT,
              "index_url": f"https://github.com/Gathin23/cleanyourtv/blob/{COMMIT}/examples/README.md",
              "index_sha256": hashlib.sha256(raw).hexdigest()}, "records": records}
    (CACHE / "failures.json").write_text(json.dumps(failures, indent=2) + "\n", encoding="utf-8")
    if failures or not records:
        raise SystemExit(f"Incomplete collection ({len(failures)} failures); existing research index was not replaced. Retry to reuse cached documents.")
    target = ROOT / "data/research-index.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    print(json.dumps({"indexed": len(records), "failed": len(failures), "source_folders": len(folders), "instructions_created": 0}))


if __name__ == "__main__":
    main()
