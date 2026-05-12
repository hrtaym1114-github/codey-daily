---
title: "Claude Code の新機能を毎日自動キャッチアップする Web アプリを作った話"
emoji: "🤖"
type: "tech"
topics: ["claudecode", "astro", "cloudflare", "githubactions", "個人開発"]
published: false
---

## TL;DR

- Claude Code の新機能（94機能、毎週増える）を**毎日5秒で発見**できるWebアプリを作った
- GitHub Actions + Claude Code Action で公式CHANGELOGを毎日自動取り込み
- 全部 **Cloudflare 無料枠** で運用、月額**実質0円**
- 🌐 https://codey.bhrtaym-blog.com
- 📦 https://github.com/hrtaym1114-github/codey-daily

---

## 動機

Claude Code を毎日使っていますが、機能追加のペースが速くてキャッチアップに苦労していました。

- 公式 CHANGELOG は長文で流し読みしにくい
- 個人ブログや Discord も追いかける時間が無い
- せっかく増えた便利機能を**知らずに使い続けている**ことが多い

「**毎朝1機能、5秒で目を通せる仕組み**」があれば自然と追従できるのでは、と考えて作ったのが Codey Daily です。

## できること

| 機能 | 説明 |
|---|---|
| 📅 今日のカード | 1日1機能を要約 + コード例で表示 |
| 🃏 フラッシュカード | 表→裏でめくって学習 |
| 🎯 クイズ | 4択で理解度チェック |
| 📜 Changelog | リリースノートをカテゴリ別検索 |
| 🔥 ストリーク | 連続学習日数を可視化（Google ログイン） |
| 🤖 自動同期 | 公式CHANGELOG を毎日取り込み |

## アーキテクチャ

```
┌──────────────────┐
│ Claude Code 公式  │
│ CHANGELOG        │
└────────┬─────────┘
         │ 毎日 03:00 JST
         ▼
┌──────────────────────────┐
│ GitHub Actions           │
│ + Claude Code Action     │ ← 差分検知して新機能抽出
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ data/features.json       │ ← Auto-PR でコミット
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Astro Static Build       │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│ Cloudflare Workers       │
│ + D1 (ストリーク管理)    │
│ + KV (セッション)        │
└──────────────────────────┘
```

## 技術スタック

- **Frontend**: Astro 6 + Tailwind CSS v4
- **Hosting**: Cloudflare Workers（静的＋一部SSR）
- **Database**: D1 (SQLite) — ユーザーストリーク管理
- **Auth**: Google OAuth (ローンチ時のみ)
- **Auto-sync**: GitHub Actions + Claude Code Action
- **Analytics**: Cloudflare Web Analytics

無料枠だけで月間PV数千〜数万まで耐えるはずです。

## ハマりポイント

### 1. CHANGELOG 差分検知が単純な diff では不安定だった

セマンティックな差分（「新コマンドが追加された」「既存コマンドの仕様変更」）が必要で、最初は正規表現でゴリゴリ書いていました。

→ **Claude Code Action に丸投げ**したら一発で解決。LLM に CHANGELOG を読ませて「新しい機能IDを features.json に追加して」と頼むだけでPRが作れる。

```yaml
# .github/workflows/changelog-sync.yml
- name: Auto-add new features (Claude Code)
  uses: anthropic/claude-code-action@v1
  with:
    prompt: |
      新しい機能カードを data/features.json に追加してください。
      テンプレートは既存エントリを参照。
```

### 2. Cloudflare Web Analytics の "Visits" が 0 になる

外部リファラなしの直接アクセスは Visits としてカウントされません。

→ 計測には GA4 を併用、もしくは独自で Workers のリクエストログを集計する設計に。

### 3. Astro 6 + Tailwind v4 + Cloudflare adapter の相性

`@astrojs/cloudflare` の `output: 'static'` モードで動かすのが最も安定。
SSR を混ぜると D1/KV bindings が build-time に評価されてしまい毎回ハマる。

## 学んだこと

- **「毎日タッチする商品」は配信ループが命**：サイトに来てもらうより、メール／RSS／プラグインで届ける方が効く（実装中）
- **Claude Code Action は強力**：曖昧な「これいい感じにして」が動く
- **Cloudflare 無料枠は本当にすごい**：D1 + KV + Workers + Web Analytics + R2 で個人開発が完結する

## これから

- [ ] 英語版（`/en/`）を自動生成
- [ ] Daily Email 配信（Resend / Loops）
- [ ] Claude Code プラグイン化（`/codey-today` スラッシュコマンド）
- [ ] リーダーボード機能

## 応援していただけると嬉しいです

- ⭐ **Star**: https://github.com/hrtaym1114-github/codey-daily
- ❤️ **Sponsor**: https://github.com/sponsors/hrtaym1114-github
- 🐦 **X**: [@Amu_Lab__](https://x.com/Amu_Lab__)

フィードバック・機能要望もぜひコメントでお待ちしています！
