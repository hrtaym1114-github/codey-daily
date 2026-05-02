# Changelog 追従ワークフロー — 運用マニュアル

## 🎯 目的
Claude Code は週に複数回バージョンアップされ、新機能が追加される。Codey Daily を常に最新の標準機能カタログに保つ自動化システム。

## 🏗 アーキテクチャ（3層）

```
[Tier 1: 即時可視化]
  ↓
GitHub raw CHANGELOG.md
  ↓ python3 scripts/fetch-changelog.py
data/changelog.json (277バージョン分の構造化データ)
  ↓
/changelog ページ で公式履歴を表示
  + python3 scripts/detect-feature-gaps.py
  ↓
data/feature-gaps.json (未追加機能リスト)
  ↓
/changelog ページ「🚨 未追加機能」バナー


[Tier 2: スケジュール検知]
  ↓
.github/workflows/changelog-sync.yml (毎日 09:00 JST cron)
  ↓
- changelog.json + feature-gaps.json を最新化
- 変更があれば main に直接 commit + redeploy
  → changelog/未追加リストが常に最新化される


[Tier 3: ヒューマンレビュー（手動）]
  ↓
ayumu が /changelog の「🚨 未追加機能」を見て判断
  ↓
- 残すべき機能を generate-standard-seed.py に追加
- python3 scripts/generate-standard-seed.py . 再実行
- D1再シード → 73件 → 80件などに拡張
  ↓
本番反映
```

## 🛠 各スクリプトの役割

| Script | 役割 | 出力 |
|---|---|---|
| `scripts/fetch-changelog.py` | GitHub raw CHANGELOG.md をパース | `data/changelog.json` |
| `scripts/detect-feature-gaps.py` | 既存DB と比較してギャップ検出 | `data/feature-gaps.json` |
| `scripts/generate-standard-seed.py` | 73機能の手動キュレーション + リンク注入 | `data/features.json` + `migrations/003_*.sql` |

## 📅 運用ルーチン

### 毎日（自動）
- 09:00 JST: GitHub Actions が changelog 同期 + 自動再デプロイ
- 結果: `/changelog` ページが最新になる

### 週1（手動・5分）
1. `/changelog` を開く → 「🚨 未追加機能」バナーを確認
2. 上位5件くらいで実際に追加すべきものをピックアップ
3. `scripts/generate-standard-seed.py` に追記:
   ```python
   {
       "id": "slash-plugin", "name": "/plugin", "category": "slash-command",
       "summary_ja": "プラグイン管理",
       "description_ja": "...",
       "examples": [{"title": "...", "code": "/plugin install ..."}],
       "links": [], "difficulty": 2, "tier": "free", "related": [],
   },
   ```
4. ローカル再生成 + 再デプロイ:
   ```bash
   cd ~/desktop/work1/codey-daily
   python3 scripts/generate-standard-seed.py .
   npx wrangler d1 execute codey-daily --local  --file=migrations/003_seed_standard_features.sql
   npx wrangler d1 execute codey-daily --remote --file=migrations/003_seed_standard_features.sql
   npx astro build && npx wrangler deploy
   git add . && git commit -m "feat: add /plugin from v2.1.126" && git push
   ```

### 月1（手動・15分）
- スキャン精度の見直し（誤検知パターン追加など）
- `SLASH_COMMAND_BLOCKLIST` 更新
- カテゴリ追加検討

## 🔐 GitHub Actions シークレット必要設定

リポジトリ Settings → Secrets and variables → Actions:

- `CLOUDFLARE_API_TOKEN` — Workers & Pages 編集権限
- `CLOUDFLARE_ACCOUNT_ID` — アカウントID
- (`GITHUB_TOKEN` は標準で付与)

## 📊 運用KPI

| 指標 | 目標 |
|---|---|
| 同期頻度 | 毎日 |
| 機能カバー率 | 90%以上（未追加 < 全機能の10%） |
| 反映ラグ | 新機能リリース → 1週間以内に追加 |

## 🧠 設計判断の根拠

### なぜ手動レビューか?
- 全自動だとサマリーの品質が崩れる（LLM API 呼び出しでも誤訳・誤分類リスク）
- 73機能のうち1つでも間違うと「公式情報源」としての信頼が落ちる
- 週5分の手動レビューで品質維持

### なぜ Tier 1 を即時可視化したか?
- /changelog ページ自体が「Codey Daily の正直さ」を担保
- 「未追加機能あります」と表示することで、ユーザーに**最新情報は公式 → このサイトは整理担当**の役割分担を明示
- 他の Claude Code 学習サイトとの差別化（透明性）

### スケーラビリティ
- 277バージョンを処理して < 1秒
- changelog.json: ~2MB、Cloudflare Workers の制限内
- ビルド時間: < 5秒（features.json + changelog.json 2ファイル）
