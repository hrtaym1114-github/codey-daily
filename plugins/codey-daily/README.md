# Codey Daily — Claude Code Plugin

Claude Code の標準機能を、ターミナルから直接発見・検索できるプラグイン。

## 提供スラッシュコマンド

| Command | 説明 |
|---|---|
| `/codey-today` | 今日の Claude Code 機能を5秒で発見 |
| `/codey-search <keyword>` | 機能を名前/カテゴリで検索 |

## 動作要件

- Claude Code (Plugin機構サポート版)
- インターネット接続（公開API `https://codey.bhrtaym-blog.com/api/...` を呼び出します）

## インストール

### Claude Code Plugin Marketplace（公開後）

```
/plugin install codey-daily
```

### ローカルインストール（先行配布）

```bash
# このリポジトリをclone
git clone https://github.com/hrtaym1114-github/codey-daily.git
cd codey-daily

# プラグインを ~/.claude/plugins/ にシンボリックリンク
mkdir -p ~/.claude/plugins
ln -s "$(pwd)/plugins/codey-daily" ~/.claude/plugins/codey-daily
```

その後 Claude Code を再起動。

## 関連リンク

- 🌐 Web版: https://codey.bhrtaym-blog.com
- 📦 Source: https://github.com/hrtaym1114-github/codey-daily
- 🐦 X: [@Amu_Lab__](https://x.com/Amu_Lab__)
- ❤️ Sponsor: https://github.com/sponsors/hrtaym1114-github

## ライセンス

MIT
