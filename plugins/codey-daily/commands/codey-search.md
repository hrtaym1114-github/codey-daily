---
description: Claude Code 機能を名前/カテゴリで検索
argument-hint: <keyword or category>
allowed-tools: Bash(curl:*)
---

Codey Daily の機能データから、ユーザー指定のキーワード `$ARGUMENTS` にマッチする機能を検索して表示してください。

## 手順

1. キーワードがカテゴリ名 (`slash-command`, `tool`, `hook`, `agent`, `skill`, `mcp`, `mode`, `file`, `cli`, `setting`) のいずれかと一致する場合:
   - `curl -s https://codey.bhrtaym-blog.com/api/category/{category}` で取得
   - 該当カテゴリの機能を一覧表示
2. それ以外の自由ワードの場合:
   - `curl -s https://codey.bhrtaym-blog.com/api/categories` で全カテゴリ取得
   - 各機能の `name`, `summary_ja` を順に取得し、キーワードを部分一致で絞り込み
   - もしくは feature データを直接取得して名前/概要にマッチを探す

## 出力フォーマット

該当機能を最大10件、以下の形式で：

```
🔍 "$ARGUMENTS" の検索結果 (N件)

1. /clear (Slash Commands) — 会話履歴をクリアして新しい状態から始める
   https://codey.bhrtaym-blog.com/feature/slash-clear/

2. ...
```

該当0件なら「該当機能なし。Codey Daily で全機能を見るには: https://codey.bhrtaym-blog.com」と案内。
