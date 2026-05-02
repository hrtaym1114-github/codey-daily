#!/usr/bin/env python3
"""
Codey Daily — 未追加機能ギャップ検出器

CHANGELOG で言及されているが Codey Daily DB にない機能を抽出
出力: data/feature-gaps.json
"""
import json
import sys
from pathlib import Path

# 誤検知を除外: パス表記、APIパス、プロジェクト名、設定ファイル等
SLASH_COMMAND_BLOCKLIST = {
    "/claude-code", "/claude-md", "/agents-md", "/onboarding-md",
    "/v1", "/v2", "/api", "/docs", "/en", "/ja",
    "/usr", "/var", "/tmp", "/bin", "/etc", "/opt", "/mnt", "/dev",
    "/home", "/root", "/private", "/Users",
    "/wsl-detect", "/wsl-distrod", "/wsl-distrobox",
    "/dev-vars", "/env", "/mcp-json",  # ファイル名
    "/null",  # /dev/null の断片
}

# 既知のCLI flag で features に含まれるが name 完全一致しないもの（重複防止）
CLI_FLAG_KNOWN = {
    "--continue", "--resume", "--print", "--model", "--add-dir",
    "--help", "--version",  # 自明すぎ
}


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    changelog_path = out_dir / "data" / "changelog.json"
    features_path = out_dir / "data" / "features.json"
    gaps_path = out_dir / "data" / "feature-gaps.json"

    if not changelog_path.exists():
        print(f"❌ {changelog_path} が無い。先に fetch-changelog.py を実行してください")
        sys.exit(1)
    if not features_path.exists():
        print(f"❌ {features_path} が無い")
        sys.exit(1)

    changelog = json.loads(changelog_path.read_text(encoding="utf-8"))
    features = json.loads(features_path.read_text(encoding="utf-8"))

    # 既存機能の名前セット
    existing_names = set()
    for f in features["features"]:
        existing_names.add(f["name"])
        # /command 形式は完全一致でも判定
        if f["name"].startswith("/"):
            existing_names.add(f["name"].split(" ")[0])  # "/clear ..." → "/clear"

    refs = changelog.get("all_references", {})
    gaps = {
        "checked_at": changelog["fetched_at"],
        "source_changelog": changelog["latest_version"],
        "missing_slash_commands": [],
        "missing_cli_flags": [],
        "missing_claude_subcommands": [],
        "missing_env_vars": [],
    }

    for cmd, info in refs.get("slash_commands", {}).items():
        if cmd in SLASH_COMMAND_BLOCKLIST:
            continue
        if cmd not in existing_names:
            gaps["missing_slash_commands"].append({
                "name": cmd,
                "first_seen": info["first_seen"],
                "first_seen_date": info["first_seen_date"],
                "last_seen": info["last_seen"],
                "mentions": info["count"],
                "categories": info["categories"],
            })

    for flag, info in refs.get("cli_flags", {}).items():
        if flag in CLI_FLAG_KNOWN:
            continue
        normalized_flag = flag
        in_features = any(normalized_flag in f["name"] for f in features["features"])
        if not in_features:
            gaps["missing_cli_flags"].append({
                "name": flag,
                "first_seen": info["first_seen"],
                "first_seen_date": info["first_seen_date"],
                "mentions": info["count"],
                "categories": info["categories"],
            })

    for subcmd, info in refs.get("claude_subcommands", {}).items():
        full_name = f"claude {subcmd}"
        in_features = any(subcmd in f["name"].lower() or full_name in f["description_ja"].lower() for f in features["features"])
        if not in_features:
            gaps["missing_claude_subcommands"].append({
                "name": full_name,
                "first_seen": info["first_seen"],
                "first_seen_date": info["first_seen_date"],
                "mentions": info["count"],
                "categories": info["categories"],
            })

    for env, info in refs.get("env_vars", {}).items():
        in_features = any(env in f["description_ja"] for f in features["features"])
        if not in_features:
            gaps["missing_env_vars"].append({
                "name": env,
                "first_seen": info["first_seen"],
                "first_seen_date": info["first_seen_date"],
                "mentions": info["count"],
                "categories": info["categories"],
            })

    # ソート: mentions 多い順
    for k in gaps:
        if k.startswith("missing_"):
            gaps[k] = sorted(gaps[k], key=lambda x: -x["mentions"])

    gaps_path.write_text(json.dumps(gaps, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 未追加機能ギャップ検出完了")
    print(f"   Slash commands  : {len(gaps['missing_slash_commands'])} 個")
    print(f"   CLI flags       : {len(gaps['missing_cli_flags'])} 個")
    print(f"   Claude subcmds  : {len(gaps['missing_claude_subcommands'])} 個")
    print(f"   Env vars        : {len(gaps['missing_env_vars'])} 個")
    print(f"\n💾 出力: {gaps_path}")

    # 上位5件を表示
    print(f"\n🔍 検討候補 TOP 5:")
    candidates = gaps["missing_slash_commands"] + gaps["missing_claude_subcommands"]
    for c in sorted(candidates, key=lambda x: -x["mentions"])[:5]:
        print(f"   {c['name']:<30} {c['mentions']}回言及  (初出: v{c['first_seen']} / {c['first_seen_date']})")


if __name__ == "__main__":
    main()
