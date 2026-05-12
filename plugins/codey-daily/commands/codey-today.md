---
description: 今日の Claude Code 機能を5秒で発見
allowed-tools: Bash(curl:*)
---

Codey Daily から「今日の機能」を取得して、見やすく整形して表示してください。

## 手順

1. `curl -s https://codey.bhrtaym-blog.com/api/today` を実行してJSONを取得
2. 取得した `feature` オブジェクトから以下を整形して表示:
   - 機能名 (`name`) と カテゴリ (`category`)
   - 概要 (`summary_ja`)
   - 詳細説明 (`description_ja`)
   - 例 (`examples`) があればコードブロックで表示
   - 関連リンク (`links`)
3. 最後に詳細URL `https://codey.bhrtaym-blog.com/feature/{feature.id}/` を案内
4. ユーザーに「もっと学びたい場合は /codey-quiz でクイズに挑戦できます」と促す（このコマンドは将来追加）

## 出力フォーマット例

```
✨ 今日の Claude Code 機能

📦 /clear  (Slash Commands)

会話履歴をクリアして新しい状態から始める

詳細: 現在のセッションの会話履歴をクリア。メモリ（永続化された情報）は保持される。
長時間のセッションで文脈をリセットしたい時に使う。

例:
  /clear

🔗 詳細: https://codey.bhrtaym-blog.com/feature/slash-clear/
```

短く、視認性高く。絵文字は1〜2個まで。
