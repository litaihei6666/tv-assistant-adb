"""Validate source records and generate a standalone offline HTML index."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load_records():
    raw = json.loads((ROOT / "data/entries.json").read_text(encoding="utf-8"))
    if set(raw) != {"schema_version", "entries"} or raw["schema_version"] != 1 or not isinstance(raw["entries"], list):
        raise ValueError("invalid catalog")
    seen = set()
    keys = {"id", "brands", "title", "scope", "models", "evidence", "status", "sources", "steps", "limitations", "transport", "reviewed_at"}
    for e in raw["entries"]:
        if not isinstance(e, dict) or set(e) != keys or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", e["id"]) or e["id"] in seen:
            raise ValueError("invalid or duplicate entry")
        seen.add(e["id"])
        if e["evidence"] not in {"official", "community", "mixed", "firsthand_report", "unverified"} or e["status"] not in {"reference", "user_report", "unresolved"} or e["transport"] not in {"unknown", "usb", "wireless"}:
            raise ValueError("invalid evidence or status")
        if not all(isinstance(e[k], str) and e[k].strip() for k in ("title", "scope", "reviewed_at")) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["reviewed_at"]):
            raise ValueError("invalid text/date")
        for k in ("brands", "models", "steps", "limitations"):
            if not isinstance(e[k], list) or not all(isinstance(x, str) and x.strip() for x in e[k]):
                raise ValueError("invalid list")
        if not e["brands"] or not e["limitations"] or not isinstance(e["sources"], list) or not e["sources"]:
            raise ValueError("missing context")
        if e["status"] == "unresolved" and e["steps"] or e["status"] != "unresolved" and not e["steps"]:
            raise ValueError("inconsistent status/steps")
        for s in e["sources"]:
            if not isinstance(s, dict) or set(s) != {"title", "url"} or not s["title"] or urlsplit(s["url"]).scheme != "https" or not urlsplit(s["url"]).hostname:
                raise ValueError("invalid source")
    return raw["entries"]


def render(entries):
    esc = lambda x: html.escape(str(x), quote=True)
    labels = {"official":"官方资料", "community":"社区资料", "mixed":"官方与社区资料", "firsthand_report":"一次用户反馈", "unverified":"资料待核实"}
    states = {"reference":"参考路径", "user_report":"用户反馈", "unresolved":"入口待确认"}
    blocks=[]
    for e in entries:
        search = " ".join([e["title"],e["scope"],*e["brands"],*e["models"]]).lower()
        steps = "".join("<li>"+esc(x)+"</li>" for x in e["steps"])
        limits = "".join("<li>"+esc(x)+"</li>" for x in e["limitations"])
        sources = "、".join("<a rel=\"noopener noreferrer\" href=\""+esc(s["url"])+"\">"+esc(s["title"])+"</a>" for s in e["sources"])
        blocks.append("<article data-search=\""+esc(search)+"\"><div class=\"badges\">"+esc(labels[e["evidence"]])+" · "+esc(states[e["status"]])+"</div><h2>"+esc(e["title"])+"</h2><p><b>适用范围：</b>"+esc(e["scope"])+"</p>"+("<h3>怎么做</h3><ol>"+steps+"</ol>" if steps else "<p><b>暂无可提供的具体步骤</b></p>")+"<h3>注意与未知</h3><ul>"+limits+"</ul><p>来源："+sources+"</p><small>资料核对："+esc(e["reviewed_at"])+"</small></article>")
    body="\n".join(blocks)
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>电视 ADB 入口资料库</title><style>body{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#f3f7f5;color:#203b37;margin:0}main{max-width:920px;margin:auto;padding:28px 20px}h1{font-size:2rem}p,li{line-height:1.65}input{box-sizing:border-box;width:100%;font-size:1.1rem;padding:14px;border:1px solid #a9bfb5;border-radius:8px}article{background:white;border:1px solid #d7e4dd;border-radius:12px;padding:20px;margin:16px 0}h2{font-size:1.25rem}h3{font-size:1rem}.badges,small{color:#397967}a{color:#166c60}#count{color:#4c6d61}.notice{background:#fff3d9;padding:14px;border-radius:8px}</style></head><body><main><h1>电视 ADB 入口资料库</h1><p>先查品牌、型号及电视实际系统；资料来源和适用范围比品牌名称更重要。</p><p class="notice">收录正在持续完善，不代表机型已实测。不要进入工厂或维修菜单；仅有 USB 调试不代表支持无线。查询只在本机进行，点击来源链接才访问外部网站。</p><label for="query">搜索品牌、型号或系统</label><input id="query" type="search" placeholder="例如 TCL、65V6D、Android TV"><p id="count" aria-live="polite"></p><section id="results">"""+body+"""</section><p>项目资料和贡献说明请查看 README.md。品牌型号只是线索，所有操作由本人决定。</p></main><script>const q=document.getElementById('query');const cards=[...document.querySelectorAll('article')];const count=document.getElementById('count');function filter(){const v=q.value.trim().toLowerCase();let n=0;for(const c of cards){const show=c.dataset.search.includes(v);c.hidden=!show;if(show)n++}count.textContent='显示 '+n+' 条参考记录'}q.addEventListener('input',filter);filter();</script></body></html>\n"""


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args()
    result=render(load_records()); target=ROOT/"index.html"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != result:
            raise SystemExit("index.html does not match source; run python scripts/build.py")
    else:
        target.write_text(result,encoding="utf-8",newline="\n")
    print("validated",len(load_records()),"records; index", "checked" if args.check else "generated")

if __name__ == "__main__": main()
