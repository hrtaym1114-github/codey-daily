# Codey Daily

> **Claude Code を毎日5秒で発見するWebアプリ。**

新機能・コマンド・Hooks・Skills まで、Claude Code の **標準機能 94** を毎朝1個ずつ発見・学習できる、開発者のための日課アプリ。

🌐 https://codey.bhrtaym-blog.com

---

## なぜ作ったか

Claude Code は週次で機能追加されますが、公式CHANGELOGは流し読みしにくく、すべてを追いかけるのは現実的ではありません。

Codey Daily は GitHub Actions が **公式CHANGELOGを毎日自動同期**し、新機能を**カードUI / フラッシュカード / クイズ**の3形式で提供します。「気づいたら新機能を使いこなせている」状態を作るのが目的です。

---

## 主な機能

| 機能 | 説明 |
|---|---|
| **📅 今日のカード** | 毎日1機能をピックアップ。5秒で読める要約 + コード例 |
| **🃏 フラッシュカード** | 表→裏でめくって学習。難易度別フィルタあり |
| **🎯 クイズ** | 4択問題で理解度チェック |
| **📜 Changelog** | 全リリースノートを検索・カテゴリ別表示 |
| **🔥 ストリーク** | 連続学習日数を可視化（Google ログイン後） |
| **🤖 自動同期** | Claude Code の新リリースをGHA + Claude Code Actionで毎日取り込み |

---

## こんな人におすすめ

- Claude Code を毎日使っているが、新機能を追いきれていない
- ターミナル外で軽くClaude Codeに触れる時間を作りたい
- スラッシュコマンドやHooksを体系的に学び直したい

---

## 技術スタック

- **Frontend**: Astro 6 + Tailwind CSS v4
- **Hosting**: Cloudflare Workers (Static + SSR)
- **Storage**: D1 (SQLite) + KV
- **Auth**: Google OAuth
- **Auto-sync**: GitHub Actions + Claude Code Action
- **Analytics**: Cloudflare Web Analytics

---

## ローカル開発

```bash
git clone https://github.com/hrtaym1114-github/codey-daily.git
cd codey-daily
npm install
npx wrangler login
npm run db:migrate
npm run dev
```

`http://localhost:4321` でアクセス可能。

### 主要スクリプト

| Command | 用途 |
|---|---|
| `npm run dev` | ローカル開発サーバ起動 |
| `npm run build` | 本番ビルド |
| `npm run preview` | 本番ビルドのプレビュー |
| `npm run deploy` | Cloudflare Pagesへデプロイ |
| `npm run extract` | 機能データ抽出 |
| `npm run db:migrate` | D1マイグレーション適用 |

---

## 自動同期ワークフロー

`.github/workflows/changelog-sync.yml` が毎日定時に実行され、Claude Code の公式CHANGELOGとの差分を検知。
新機能が見つかると Claude Code Action が自動で feature ページを生成・PRを作成します。

詳細は [`CHANGELOG-WORKFLOW.md`](./CHANGELOG-WORKFLOW.md) を参照。

---

## 応援する

開発は個人で進めています。応援していただける方はぜひ：

- ⭐ **Star this repo** ↑右上のStarボタン
- ❤️ **[GitHub Sponsors](https://github.com/sponsors/hrtaym1114-github)**
- 🐦 **X でシェア**: [@Amu_Lab__](https://x.com/Amu_Lab__)

---

## ライセンス

MIT
