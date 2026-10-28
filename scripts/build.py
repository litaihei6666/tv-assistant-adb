"""Validate source records and generate a standalone offline HTML index."""
import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/litaihei6666/tv-assistant-adb"


def issue_link(template, title):
    return REPOSITORY + "/issues/new?" + urlencode({"template": template, "title": title[:180]})


def render_help_wanted(entries, research=()):
    def cell(value):
        return html.escape(str(value), quote=False).replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")
    pending = [e for e in entries if e["status"] == "unresolved"]
    lines = ["# 哪些设备正在等你补充", "",
             "有自己的设备、原始资料或已经遇到的失败情况，都可以参与；不要求会写代码，也不要求为投稿额外测试。未知就写未知，不进入工厂或维修菜单。", "",
             "## 优先补什么", "",
             "- 国内定制电视的完整型号、固件与普通设置入口，尤其是同型号不同地区和升级前后的差异。",
             "- Android 4.4等旧机：区分电视固件号与Android版本，说明实际连接方式；没有安全入口也可以反馈。",
             "- 运营商盒子：除型号外注明运营商和地区，不照抄其他固件的菜单。",
             "- 已获得权限的本人图解、失效教程、品牌归属错误和能直接核对的原始来源。", "",
             f"## 当前{len(pending)}条入口待确认记录", "",
             "此表由data/entries.json生成。点击对应项只会打开待填写的GitHub表单，不会自动投稿或改变资料状态。", "",
             "| 待补充条目 | 条目ID | 参与入口 |", "| --- | --- | --- |"]
    for e in pending:
        link = issue_link("model-report.yml", "[设备补充] " + e["id"] + " " + e["title"])
        lines.append(f"| {cell(e['title'])} | {e['id']} | [我有这台设备或资料]({link}) |")
    lines += ["", f"## 另外{len(research)}条机型来源索引怎样参与", "",
              "来源索引只是一批待审查线索，和上表或已整理记录可能重叠。你可以按品牌搜索自己的设备，对照原文，补充它最初怎样开启ADB；仅有已连接后的使用记录不足以生成入口教程。索引条数以当前data/research-index.json为准。", "",
              f"[打开投稿入口]({REPOSITORY}/issues/new/choose) · [如何投稿、拍图及授权](../CONTRIBUTING.md) · [完整覆盖情况](COVERAGE.md)", "",
              "维护者审核后再更新数据库和查询页，未知或矛盾不会自动变为支持；愿意署名的已采纳贡献可登记到社区贡献名单。", ""]
    return "\n".join(lines)


def load_aliases():
    aliases = json.loads((ROOT / "data/brand-aliases.json").read_text(encoding="utf-8"))
    if not isinstance(aliases, dict) or not all(isinstance(k, str) and k.strip() and isinstance(v, list) and v and all(isinstance(x, str) and x.strip() for x in v) for k, v in aliases.items()):
        raise ValueError("Invalid brand aliases")
    return aliases


def brand_terms(brands, aliases):
    terms = list(brands)
    wanted = {x.casefold() for x in brands}
    for name, variants in aliases.items():
        family = [name, *variants]
        if wanted.intersection(x.casefold() for x in family):
            terms.extend(family)
    return " ".join(dict.fromkeys(terms))


def load_records():
    raw = json.loads((ROOT / "data/entries.json").read_text(encoding="utf-8"))
    if set(raw) != {"schema_version", "entries"} or raw["schema_version"] != 1 or not isinstance(raw["entries"], list):
        raise ValueError("invalid catalog")
    seen = set()
    keys = {"id", "brands", "title", "scope", "models", "evidence", "status", "sources", "steps", "limitations", "transport", "reviewed_at"}
    for e in raw["entries"]:
        if not isinstance(e, dict) or not keys <= set(e) or not set(e) <= keys | {"context"} or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", e["id"]) or e["id"] in seen:
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
        if "context" in e:
            context = e["context"]
            if not isinstance(context, dict) or set(context) != {"system", "firmware", "region"} or not all(isinstance(v, str) and v.strip() for v in context.values()):
                raise ValueError("invalid device context")
        for s in e["sources"]:
            if not isinstance(s, dict) or set(s) != {"title", "url"} or not s["title"] or urlsplit(s["url"]).scheme != "https" or not urlsplit(s["url"]).hostname:
                raise ValueError("invalid source")
    return raw["entries"]


def load_research():
    path = ROOT / "data/research-index.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"schema_version", "source", "records"} or data.get("schema_version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("Invalid research index")
    source = data.get("source", {})
    if not isinstance(source, dict) or set(source) != {"repository", "commit", "index_url", "index_sha256"}:
        raise ValueError("Invalid research source")
    commit = source.get("commit", "")
    if source.get("repository") != "Gathin23/cleanyourtv" or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{8,40}", commit):
        raise ValueError("Unpinned research source")
    if source["index_url"] != f"https://github.com/Gathin23/cleanyourtv/blob/{commit}/examples/README.md" or not isinstance(source["index_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", source["index_sha256"]):
        raise ValueError("Invalid source index provenance")
    seen = set()
    for row in data["records"]:
        if not isinstance(row, dict) or set(row) != {"id", "brand", "title", "system", "source_url", "metadata_sha256", "status"}:
            raise ValueError("Unexpected research fields")
        if not isinstance(row["id"], str) or not re.fullmatch(r"[a-z0-9-]+", row["id"]) or row["id"] in seen:
            raise ValueError("Invalid research id")
        seen.add(row["id"])
        expected = f"https://github.com/Gathin23/cleanyourtv/blob/{commit}/examples/{row['id']}/debloat.txt"
        if row["status"] != "unreviewed" or row["source_url"] != expected or not isinstance(row["metadata_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", row["metadata_sha256"]):
            raise ValueError("Research cannot become an instruction")
        if not all(isinstance(row[key], str) and 0 < len(row[key]) <= 1500 for key in ("brand", "title", "system")):
            raise ValueError("Invalid research metadata")
    return data["records"]


def render(entries, research=()):
    esc = lambda x: html.escape(str(x), quote=True)
    aliases = load_aliases()
    labels = {"official":"官方资料", "community":"社区资料", "mixed":"官方与社区资料", "firsthand_report":"一次用户反馈", "unverified":"资料待核实"}
    states = {"reference":"参考路径", "user_report":"用户反馈", "unresolved":"入口待确认"}
    blocks=[]
    for e in entries:
        context = e.get("context", {})
        search = " ".join([e["title"],e["scope"],brand_terms(e["brands"], aliases),*e["models"],*context.values()]).lower()
        details = ""
        if context:
            details = "<p><b>资料中的设备：</b>" + "；".join(esc(name) + "：" + esc(context[key]) for key, name in (("system", "系统"), ("firmware", "固件"), ("region", "地区"))) + "</p>"
        steps = "".join("<li>"+esc(x)+"</li>" for x in e["steps"])
        limits = "".join("<li>"+esc(x)+"</li>" for x in e["limitations"])
        sources = "、".join("<a rel=\"noopener noreferrer\" href=\""+esc(s["url"])+"\">"+esc(s["title"])+"</a>" for s in e["sources"])
        correction = esc(issue_link("correction.yml", "[纠错] " + e["id"] + " " + e["title"]))
        blocks.append("<article data-search=\""+esc(search)+"\"><div class=\"badges\">"+esc(labels[e["evidence"]])+" · "+esc(states[e["status"]])+"</div><h2>"+esc(e["title"])+"</h2><p><b>适用范围：</b>"+esc(e["scope"])+"</p>"+details+("<h3>怎么做</h3><ol>"+steps+"</ol>" if steps else "<p><b>暂无可提供的具体步骤</b></p>")+"<h3>注意与未知</h3><ul>"+limits+"</ul><p>来源："+sources+"</p><small>资料核对："+esc(e["reviewed_at"])+"</small><p><a rel=\"noopener noreferrer\" href=\""+correction+"\">纠正这条资料或补充固件差异</a></p></article>")
    body="\n".join(blocks)
    research_blocks = []
    for row in research:
        search = " ".join((brand_terms([row["brand"]], aliases), row["title"], row["system"])).lower()
        contribution = esc(issue_link("model-report.yml", "[设备补充] " + row["title"]))
        research_blocks.append('<article data-kind="research" data-search="' + esc(search) + '"><div class="badges">机型来源索引 · 未审查 · 无操作步骤</div><h2>' + esc(row["title"]) + '</h2><p>来源品牌标签：' + esc(row["brand"]) + '；系统：' + esc(row["system"]) + '</p><p>只说明该来源存在机型记录，不代表已有可用的开启教程。原页面可能包含不适合普通用户的系统操作，不要直接照做。</p><a rel="noopener noreferrer" href="' + esc(row["source_url"]) + '">查看固定版本来源</a><p><a rel="noopener noreferrer" href="' + contribution + '">我有这台设备，可以补充入口或图解</a></p></article>')
    body += '<details id="research"><summary>机型资料来源索引：' + str(len(research)) + ' 条（待逐条审查，不计为可用教程）</summary>' + ''.join(research_blocks) + '</details>'
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>电视 ADB 入口资料库</title><style>body{font-family:system-ui,'Microsoft YaHei',sans-serif;background:#f3f7f5;color:#203b37;margin:0}main{max-width:920px;margin:auto;padding:28px 20px}h1{font-size:2rem}p,li{line-height:1.65}input{box-sizing:border-box;width:100%;font-size:1.1rem;padding:14px;border:1px solid #a9bfb5;border-radius:8px}article{background:white;border:1px solid #d7e4dd;border-radius:12px;padding:20px;margin:16px 0}h2{font-size:1.25rem}h3{font-size:1rem}.badges,small{color:#397967}a{color:#166c60}.contribute{background:#e4f1e9;border:1px solid #b7d1c1;border-radius:12px;padding:18px;margin:20px 0}.action-list{display:flex;flex-wrap:wrap;gap:10px}.action-list a{background:#fff;border:1px solid #93b5a5;border-radius:8px;padding:10px;text-decoration:none}.action-list a:focus-visible{outline:3px solid #174f40}#count{color:#4c6d61}.notice{background:#fff3d9;padding:14px;border-radius:8px}</style></head><body><main><h1>电视 ADB 入口资料库</h1><p>先查品牌、型号及电视实际系统；资料来源和适用范围比品牌名称更重要。</p><p class="notice">收录正在持续完善，不代表机型已实测。不要进入工厂或维修菜单；仅有 USB 调试不代表支持无线。查询只在本机进行，点击来源或贡献链接才访问外部网站。</p><aside class="contribute"><h2>一起补齐各品牌、各型号的入口</h2><p>不需要懂代码。知道怎么打开、遇到失败，或有自己拍的图解，都欢迎补充。未知可以直接写未知。</p><div class="action-list"><a href="https://github.com/litaihei6666/tv-assistant-adb/issues/new?template=model-report.yml">补充我的设备</a><a href="https://github.com/litaihei6666/tv-assistant-adb/issues/new?template=correction.yml">纠正教程</a><a href="https://github.com/litaihei6666/tv-assistant-adb/issues/new?template=source-lead.yml">提交资料线索</a></div><p>点击后到GitHub登录并填写表单，由本人提交；资料先审核再收录。图片请用本人拍摄、已打码且有权授权的内容。</p><a href="https://github.com/litaihei6666/tv-assistant-adb/blob/main/docs/HELP_WANTED.md">看看哪些设备正在等补充</a></aside><label for="query">搜索品牌、型号或系统</label><input id="query" type="search" placeholder="例如 TCL、65V6D、Android TV"><p id="count" aria-live="polite"></p><section id="results">"""+body+"""</section><p>项目资料和贡献说明请查看 README.md。品牌型号只是线索，所有操作由本人决定。</p></main><script>const q=document.getElementById('query');const cards=[...document.querySelectorAll('article')];const count=document.getElementById('count');function filter(){const v=q.value.trim().toLowerCase();let n=0;let r=0;for(const c of cards){const show=c.dataset.search.includes(v);c.hidden=!show;if(show){if(c.dataset.kind==='research')r++;else n++}}count.textContent='显示 '+n+' 条已整理记录；'+r+' 条待审查机型资料';const panel=document.getElementById('research');if(panel)panel.open=Boolean(v&&r&&!n)}q.addEventListener('input',filter);filter();</script></body></html>\n"""


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args=parser.parse_args()
    entries, research = load_records(), load_research()
    outputs = {ROOT / "index.html": render(entries, research), ROOT / "docs/HELP_WANTED.md": render_help_wanted(entries, research)}
    for target, result in outputs.items():
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != result:
                raise SystemExit(f"{target.name} does not match source; run python scripts/build.py")
        else:
            target.write_text(result, encoding="utf-8", newline="\n")
    print("validated", len(entries), "records; page and help list", "checked" if args.check else "generated")

if __name__ == "__main__": main()
