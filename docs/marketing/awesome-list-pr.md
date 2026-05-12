# Awesome リスト向け PR テンプレート

## ターゲットリスト

| Repo | Section | URL |
|---|---|---|
| `hesreallyhim/awesome-claude-code` | Tools / Learning | https://github.com/hesreallyhim/awesome-claude-code |
| `langgptai/awesome-claude` | Resources | https://github.com/langgptai/awesome-claude |
| `awesome-anthropic` | Community Tools | （要検索） |
| `awesome-ai-tools` | Coding | https://github.com/mahseema/awesome-ai-tools |
| `awesome-llm-apps` | Productivity | https://github.com/Shubhamsaboo/awesome-llm-apps |

> 投稿前に各リポジトリの CONTRIBUTING.md を確認すること。
> アルファベット順 or カテゴリ順を遵守。

---

## 推奨エントリ（短い版）

```markdown
- [Codey Daily](https://codey.bhrtaym-blog.com) — Daily 5-second discovery app for Claude Code's 94 standard features. Auto-synced to the official CHANGELOG. Flashcards, quizzes, streak tracking. ([source](https://github.com/hrtaym1114-github/codey-daily))
```

## 推奨エントリ（やや長い版、説明欄が長いリスト用）

```markdown
- **[Codey Daily](https://codey.bhrtaym-blog.com)** — A daily learning app that surfaces one Claude Code feature per day. All 94 standard features (slash commands, hooks, agents, skills, MCP, settings) auto-synced from the official CHANGELOG via GitHub Actions + Claude Code Action. Includes flashcards, quizzes, and streak tracking. Runs on Cloudflare Workers. Open source ([repo](https://github.com/hrtaym1114-github/codey-daily)).
```

---

## PR 本文テンプレート

```markdown
## Add Codey Daily — daily Claude Code feature discovery app

I'd like to propose adding **Codey Daily** to this list under the [Tools / Learning] section.

**What it is**: A web app that surfaces one Claude Code feature per day, with flashcards, quizzes, and a searchable changelog. All 94 standard features are auto-synced from the official CHANGELOG.

**Why it fits**: It directly helps Claude Code users keep up with the rapid release cadence — a common pain point in the community.

**Links**:
- Live: https://codey.bhrtaym-blog.com
- Source: https://github.com/hrtaym1114-github/codey-daily
- License: MIT

The entry follows this list's existing format and is placed alphabetically under [Section].

Thanks for maintaining this list!
```

---

## 投稿手順

1. リポジトリをfork
2. `README.md` または該当ファイルを編集（アルファベット順を維持）
3. ブランチ作成（例：`add-codey-daily`）
4. PR作成、上記テンプレを使用
5. CI（リンクチェック等）が通ることを確認
6. メンテナーの返信を待つ（数日〜数週間）

---

## 採択率を上げるコツ

- **既存エントリと同じフォーマット**を厳守（メンテナーは形式バラつきを嫌う）
- **誇大表現を避ける**（"the best", "revolutionary" 等はNG）
- **ライセンス明記**（OSS リスト多くは OSS必須）
- **アルファベット順 / カテゴリ整合性**を守る
- リポジトリにスクショやGIFがあると審査が早い → README ポリッシュ済み（#6 完了）が活きる
