# AI系ニュースレター ピッチ

## ターゲット（優先順）

| Newsletter | 想定読者 | 推奨アプローチ |
|---|---|---|
| Ben's Bites | AI tools全般 | Tipsフォームから submit |
| TLDR AI | デベロッパー寄り | submission form |
| The Rundown AI | 一般AI | カジュアルtweet+メール |
| AlphaSignal | エンジニア | curated list狙い |
| Import AI (Jack Clark) | 研究系 | (該当しない可能性高) |
| The Neuron | プロダクトピープル | submission form |
| AI Tool Report | tooling向け | tooling submission |

> **どこに送るかより、誰の手元に届けるか**。Anthropic/Claudeコミュニティに近い読者基盤を持つメディアに絞る。

---

## ピッチメール（テンプレート）

**Subject**: `Codey Daily — daily Claude Code feature discovery (built solo, open source)`

```
Hi [Editor name or "team"],

I'm a solo developer and a heavy Claude Code user. I just shipped a small
side project I think your readers might find useful.

**Codey Daily** (https://codey.bhrtaym-blog.com) is a daily
discovery app for Claude Code's 94 standard features. One feature per day,
flashcards, quizzes, and a searchable changelog — all auto-synced to the
official CHANGELOG via GitHub Actions + Claude Code Action.

The hook: Claude Code ships fast, and most users miss new features for
weeks. Codey Daily turns "keeping up" into a 5-second daily habit.

It's open source (MIT), runs entirely on Cloudflare's free tier, and the
auto-sync workflow itself is a fun example of "delegate the boring work
to Claude Code Action."

Source: https://github.com/hrtaym1114-github/codey-daily

I'd be honored if it fit your "Tools" / "Cool projects" / "Daily picks"
section. Happy to provide a 100-word blurb, screenshots, or a custom
description in your house style — just let me know.

Thanks for what you do. Best newsletter in the space.

— [Your name]
[Your X / GitHub]
```

---

## プレスキット（添付できる素材）

```
docs/marketing/press-kit/
├── og.png             ← 既存
├── screenshot-home.png    （要撮影）
├── screenshot-flashcard.png （要撮影）
├── screenshot-changelog.png （要撮影）
├── demo.gif           （要撮影：トップ→フラッシュ→クイズの一連）
└── tagline.txt        ← 1行説明
```

### tagline.txt（1行版）

```
Codey Daily — Discover one Claude Code feature every day. Auto-synced from the official CHANGELOG. Free & open source.
```

### 100語ブレーバー（短文）

```
Codey Daily turns Claude Code's fast-moving CHANGELOG into a 5-second
daily habit. The web app surfaces one of 94 standard features per day,
with flashcards, quizzes, and a searchable changelog. Auto-synced via
GitHub Actions + Claude Code Action — the bot writes its own PRs.
Built solo on Astro + Cloudflare Workers, runs on free tier.
Open source under MIT.
```

### 50語ブレーバー（極短文）

```
Codey Daily is a daily discovery app for Claude Code's 94 standard
features. One per day, plus flashcards, quizzes, and a searchable
changelog auto-synced via GitHub Actions. Solo-built, open source.
```

---

## フォローアップ運用

- 送信後 7日間返信なし → やんわりリマインダー1通
- 採択された場合：掲載日に X で必ず告知してニュースレター側のリーチを増幅
- 不採択でも丁寧に Thank you 返信（次回他のプロダクトでも有効な関係構築）
