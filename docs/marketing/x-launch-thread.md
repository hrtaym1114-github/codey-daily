# X (Twitter) ローンチスレッド ドラフト

> 投稿前チェック：
> - [ ] サイトURLは独自ドメイン化済みか確認（または workers.dev で先行投稿）
> - [ ] OG画像が正しく表示されるか https://cards-dev.twitter.com/validator で検証
> - [ ] GIF/動画3〜5本を `assets/` に準備
> - [ ] スレッドの最後に応援リクエスト（Star/Sponsor）

---

## 投稿1（フック / 導入）

```
個人開発でClaude Codeの新機能を毎日5秒で発見できるWebアプリを作りました 🎉

『Codey Daily』
👉 https://codey.bhrtaym-blog.com

毎朝1機能をカードで発見、フラッシュカードで定着、クイズで腕試し。
Claude Code の標準機能 94 を網羅、自動同期で常に最新です。

スレッドで詳細紹介します🧵
```
**添付**: トップページのGIF（カード切替＋ストリーク表示）

---

## 投稿2（解決する課題）

```
Claude Code、毎週のように新機能が増えてキャッチアップが大変ですよね。

公式CHANGELOGは長文で流し読みしにくく、Discordや個人ブログを巡回するのも限界がある。

Codey Daily は GitHub Actions が公式CHANGELOGを毎日自動同期し、新機能を3形式（カード/フラッシュ/クイズ）でお届けします。
```
**添付**: Changelog → 自動取り込み → カード生成のフロー図 or GIF

---

## 投稿3（主要機能）

```
主な機能：

📅 今日のカード：5秒で読める要約 + コード例
🃏 フラッシュカード：表→裏でめくって学習
🎯 クイズ：4択で理解度チェック
🔥 ストリーク：連続学習日数を可視化
📜 Changelog：全リリースをカテゴリ別に検索
🤖 自動同期：新リリースをGHA + Claude Code Action で取り込み
```
**添付**: 各機能スクリーンショット4枚グリッド

---

## 投稿4（技術スタック）

```
技術スタック：
- Astro 6 + Tailwind v4
- Cloudflare Workers (Static + SSR)
- D1 (SQLite) + KV
- Google OAuth
- GitHub Actions + Claude Code Action（自動同期）

ぜんぶ無料枠 or ほぼゼロ円で動かせます。コードは完全公開：
👉 https://github.com/hrtaym1114-github/codey-daily
```
**添付**: アーキテクチャ図

---

## 投稿5（クロージング / 応援）

```
個人で作ってます。応援していただける方は：

⭐ Star: https://github.com/hrtaym1114-github/codey-daily
❤️ Sponsor: https://github.com/sponsors/hrtaym1114-github
🔁 RT/シェア大歓迎です！

フィードバック・要望もぜひコメントで教えてください 🙏
```

---

## メンション候補（ターゲット）

### 国内（日本語）
- AI開発系インフルエンサー（Claude Code 利用者）
- Zenn / Qiita でClaude Code記事を書いている方
- 個人開発界隈のフォロワー多めの方

### 海外（英語ローンチ時）
- @AnthropicAI（公式）
- @alexalbert__（Anthropic DevRel）
- Claude Code 関連のオープンソース作者
- AI tooling 系ニュースレター運営者

---

## ハッシュタグ

```
#ClaudeCode #AI開発 #個人開発 #IndieHacker #BuildInPublic
```

英語版は `#ClaudeCode #AItools #IndieHackers #BuildInPublic`

---

## 投稿後アクション

1. ピン留め（プロフィール最上段）
2. 反応の多いリプには丁寧に返信
3. 24時間以内に **「初日数字」追跡ツイート**（UV、X engagement）
4. 1週間後 **「学んだこと」振り返りツイート**（再拡散の起点に）
