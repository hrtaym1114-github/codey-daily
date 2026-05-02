#!/usr/bin/env python3
"""
Codey Daily — Claude Code 公式 CHANGELOG パーサ

Source: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md

役割:
1. CHANGELOG.md を取得
2. <Update label=...> ブロックを抽出
3. 各エントリをカテゴリ分類（Added / Fixed / Security / Improved）
4. 機能名（/command, env vars, tool names等）を抽出
5. data/changelog.json として保存
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
DOCS_PAGE = "https://code.claude.com/docs/en/changelog"

# 抽出対象機能名のパターン
SLASH_CMD_RE = re.compile(r'`?(/[a-z][a-z0-9-]+)`?')
ENV_VAR_RE = re.compile(r'`([A-Z][A-Z0-9_]{3,})`')
CLI_FLAG_RE = re.compile(r'`(--[a-z][a-z-]+)`')
CLAUDE_SUBCMD_RE = re.compile(r'`claude\s+([a-z][a-z-]+)`')


def fetch_changelog() -> str:
    req = urllib.request.Request(CHANGELOG_URL, headers={"User-Agent": "codey-daily/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def parse_date(date_str: str) -> str:
    """'May 1, 2026' → '2026-05-01'"""
    try:
        dt = datetime.strptime(date_str.strip(), "%B %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str  # フォールバック


def categorize_entry(text: str) -> str:
    t = text.lower().strip()
    if t.startswith("**security:**") or "security:" in t[:20]:
        return "security"
    if t.startswith("fixed") or t.startswith("fix "):
        return "fixed"
    if t.startswith("added") or t.startswith("new ") or "**added**" in t[:30]:
        return "added"
    if t.startswith("improved") or t.startswith("enhanced"):
        return "improved"
    if t.startswith("removed") or t.startswith("deprecated"):
        return "removed"
    if t.startswith("changed") or t.startswith("renamed"):
        return "changed"
    # 動詞ベース判定
    if "added " in t[:50] or "now supports" in t[:60] or "now lists" in t[:60]:
        return "added"
    return "other"


def extract_references(text: str) -> dict:
    """エントリから機能名を抽出"""
    return {
        "slash_commands": list(set(SLASH_CMD_RE.findall(text))),
        "env_vars": list(set(ENV_VAR_RE.findall(text))),
        "cli_flags": list(set(CLI_FLAG_RE.findall(text))),
        "claude_subcommands": list(set(CLAUDE_SUBCMD_RE.findall(text))),
    }


def parse_changelog(md: str) -> list:
    """## VERSION ヘッダで区切られたマークダウンを抽出"""
    versions = []

    # ## VERSION (e.g., ## 2.1.126) を見つけて分割
    sections = re.split(r'\n## ([\d.]+)\s*\n', md)
    # sections[0] は "# Changelog" などのヘッダ
    # sections[1::2] = version numbers
    # sections[2::2] = body content

    for i in range(1, len(sections) - 1, 2):
        version = sections[i].strip()
        body = sections[i + 1].strip() if i + 1 < len(sections) else ""

        # bullet point を抽出
        entries = []
        for raw_line in body.split("\n"):
            line = raw_line.strip()
            # `- ` or `* ` で始まるエントリ。「- - 」のような誤入力もサポート
            m = re.match(r'^[-*]\s+(?:[-*]\s+)?(.+)', line)
            if m:
                content = m.group(1).strip()
                if content:
                    refs = extract_references(content)
                    entries.append({
                        "text": content,
                        "category": categorize_entry(content),
                        "refs": refs,
                    })

        versions.append({
            "version": version,
            "date_raw": None,           # raw markdownには日付なし
            "date": None,                # 後でGitHub APIで補完可能
            "entries": entries,
            "stats": {
                "total": len(entries),
                "added": sum(1 for e in entries if e["category"] == "added"),
                "fixed": sum(1 for e in entries if e["category"] == "fixed"),
                "security": sum(1 for e in entries if e["category"] == "security"),
                "improved": sum(1 for e in entries if e["category"] == "improved"),
                "other": sum(1 for e in entries if e["category"] not in ("added", "fixed", "security", "improved")),
            },
        })

    return versions


def aggregate_references(versions: list) -> dict:
    """全バージョン横断で「変更があった機能名」を集計"""
    all_refs = {
        "slash_commands": {},
        "env_vars": {},
        "cli_flags": {},
        "claude_subcommands": {},
    }
    for v in versions:
        for entry in v["entries"]:
            for kind, items in entry["refs"].items():
                for item in items:
                    if item not in all_refs[kind]:
                        all_refs[kind][item] = {
                            "count": 0,
                            "first_seen": v["version"],
                            "first_seen_date": v["date"],
                            "last_seen": v["version"],
                            "last_seen_date": v["date"],
                            "categories": [],
                        }
                    all_refs[kind][item]["count"] += 1
                    all_refs[kind][item]["last_seen"] = v["version"]
                    all_refs[kind][item]["last_seen_date"] = v["date"]
                    if entry["category"] not in all_refs[kind][item]["categories"]:
                        all_refs[kind][item]["categories"].append(entry["category"])
    return all_refs


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    out_path = out_dir / "data" / "changelog.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📥 Fetching {CHANGELOG_URL}")
    md = fetch_changelog()
    print(f"   ({len(md):,} chars)")

    versions = parse_changelog(md)
    refs = aggregate_references(versions)

    payload = {
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "source_url": CHANGELOG_URL,
        "docs_url": DOCS_PAGE,
        "version_count": len(versions),
        "latest_version": versions[0]["version"] if versions else None,
        "latest_date": versions[0]["date"] if versions else None,
        "versions": versions,
        "all_references": refs,
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ {len(versions)} versions parsed")
    if versions:
        print(f"   Latest: v{versions[0]['version']}")
        print(f"   Oldest: v{versions[-1]['version']}")

    # 集計サマリ
    totals = {"added": 0, "fixed": 0, "security": 0, "improved": 0, "other": 0}
    for v in versions:
        for k in totals:
            totals[k] += v["stats"].get(k, 0)
    print(f"\n📊 全エントリ集計:")
    for k, n in totals.items():
        print(f"   {k}: {n}")

    print(f"\n📌 検出された機能名:")
    for kind, items in refs.items():
        if items:
            print(f"   {kind}: {len(items)} 個")

    print(f"\n💾 出力: {out_path}")


if __name__ == "__main__":
    main()
