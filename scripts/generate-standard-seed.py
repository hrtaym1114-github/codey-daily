#!/usr/bin/env python3
"""
Codey Daily — Claude Code 標準機能の初期データ生成

ayumu 自作のVault素材ではなく、Claude Code 組み込み機能のキュレーションを生成。
"""
import json
import sys
from pathlib import Path

# ============================================================
# 公式ドキュメントURL（カテゴリ→URL）
# ※ 2026-05 時点で確認済: code.claude.com/docs/en/
# ============================================================
DOCS_BASE = "https://code.claude.com/docs/en"
CATEGORY_DOCS_URL = {
    "slash-command": f"{DOCS_BASE}/commands",
    "tool": f"{DOCS_BASE}/tools-reference",
    "hook": f"{DOCS_BASE}/hooks",
    "agent": f"{DOCS_BASE}/sub-agents",
    "skill": f"{DOCS_BASE}/skills",
    "mcp": f"{DOCS_BASE}/mcp",
    "mode": f"{DOCS_BASE}/permission-modes",
    "file": f"{DOCS_BASE}/memory",
    "cli": f"{DOCS_BASE}/cli-reference",
    "setting": f"{DOCS_BASE}/settings",
}

# 個別オーバーライド（より具体的なページがある場合）
FEATURE_DOCS_URL = {
    "file-claude-md": f"{DOCS_BASE}/memory",
    "file-agents-md": f"{DOCS_BASE}/memory",
    "file-onboarding-md": f"{DOCS_BASE}/memory",
    "file-settings-json": f"{DOCS_BASE}/settings",
    "file-settings-local-json": f"{DOCS_BASE}/settings",
    "file-mcp-json": f"{DOCS_BASE}/mcp",
    "file-memory": f"{DOCS_BASE}/memory",
    "file-mention": f"{DOCS_BASE}/memory",
    "mode-plan": f"{DOCS_BASE}/permission-modes",
    "mode-permission": f"{DOCS_BASE}/permission-modes",
    "mode-output-style": f"{DOCS_BASE}/output-styles",
    "mode-headless": f"{DOCS_BASE}/cli-reference",
    "misc-statusline": f"{DOCS_BASE}/statusline",
    "misc-keybindings": f"{DOCS_BASE}/settings",
    "misc-ide-vscode": f"{DOCS_BASE}/vs-code",
    "misc-ide-jetbrains": f"{DOCS_BASE}/jetbrains",
    "misc-fast-mode": f"{DOCS_BASE}/cli-reference",
    "skill-overview": f"{DOCS_BASE}/skills",
    "skill-structure": f"{DOCS_BASE}/skills",
    "skill-marketplace": f"{DOCS_BASE}/discover-plugins",
    "skill-trigger": f"{DOCS_BASE}/skills",
    "agent-subagent": f"{DOCS_BASE}/sub-agents",
    "agent-explore": f"{DOCS_BASE}/sub-agents",
    "agent-plan": f"{DOCS_BASE}/sub-agents",
    "agent-general-purpose": f"{DOCS_BASE}/sub-agents",
    "agent-custom": f"{DOCS_BASE}/sub-agents",
    "agent-isolation": f"{DOCS_BASE}/agent-teams",
    "mcp-overview": f"{DOCS_BASE}/mcp",
    "mcp-stdio": f"{DOCS_BASE}/mcp",
    "mcp-sse": f"{DOCS_BASE}/mcp",
    "mcp-http": f"{DOCS_BASE}/mcp",
}


def get_doc_url(feature_id: str, category: str) -> str:
    """個別オーバーライド優先、なければカテゴリ既定"""
    return FEATURE_DOCS_URL.get(feature_id, CATEGORY_DOCS_URL.get(category, DOCS_BASE))


# ============================================================
# 標準機能データ
# ============================================================
FEATURES = [
    # ========== Slash Commands (built-in) ==========
    {
        "id": "slash-clear", "name": "/clear", "category": "slash-command",
        "summary_ja": "会話履歴をクリアして新しい状態から始める",
        "description_ja": "現在のセッションの会話履歴をクリア。メモリ（永続化された情報）は保持される。長時間のセッションで文脈をリセットしたい時に使う。",
        "examples": [{"title": "履歴クリア", "code": "/clear"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-help", "name": "/help", "category": "slash-command",
        "summary_ja": "利用可能なコマンド一覧を表示",
        "description_ja": "Claude Code で使える組み込みコマンドの一覧を表示。困ったらまずこれ。",
        "examples": [{"title": "ヘルプ表示", "code": "/help"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-memory", "name": "/memory", "category": "slash-command",
        "summary_ja": "メモリーシステムを管理",
        "description_ja": "ユーザーの好み、プロジェクトの背景、フィードバックなどを永続的に蓄積するメモリーシステムを管理。将来の対話で自動的に参照される。",
        "examples": [{"title": "メモリ確認", "code": "/memory"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["file-claude-md"],
    },
    {
        "id": "slash-agents", "name": "/agents", "category": "slash-command",
        "summary_ja": "サブエージェントを管理",
        "description_ja": "サブエージェントの定義・起動・状態確認。複雑なタスクを並列実行する際に使う。Task tool と組み合わせる。",
        "examples": [{"title": "エージェント一覧", "code": "/agents"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["tool-task", "agent-subagent"],
    },
    {
        "id": "slash-context", "name": "/context", "category": "slash-command",
        "summary_ja": "コンテキストウィンドウ使用率を表示",
        "description_ja": "現在のセッションでのコンテキスト使用率を確認。長時間セッションでの圧縮タイミング判断に役立つ。",
        "examples": [{"title": "使用量確認", "code": "/context"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-compact"],
    },
    {
        "id": "slash-hooks", "name": "/hooks", "category": "slash-command",
        "summary_ja": "フック設定を管理",
        "description_ja": "PreToolUse/PostToolUse/Stop等のイベントで自動実行するシェルスクリプトを設定。",
        "examples": [{"title": "フック確認", "code": "/hooks"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["hook-pretooluse", "hook-posttooluse"],
    },
    {
        "id": "slash-init", "name": "/init", "category": "slash-command",
        "summary_ja": "CLAUDE.md を初期化",
        "description_ja": "現在のリポジトリを分析して CLAUDE.md（プロジェクトガイダンスファイル）の雛形を生成。",
        "examples": [{"title": "初期化", "code": "/init"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["file-claude-md"],
    },
    {
        "id": "slash-review", "name": "/review", "category": "slash-command",
        "summary_ja": "プルリクエストをレビュー",
        "description_ja": "現在のブランチまたは指定PRをレビュー。コード品質、バグ可能性、改善提案を返す。",
        "examples": [{"title": "PRレビュー", "code": "/review"}],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-config", "name": "/config", "category": "slash-command",
        "summary_ja": "設定を表示・変更",
        "description_ja": "テーマ、モデル、その他のユーザー設定を変更。settings.json の代替インタフェース。",
        "examples": [{"title": "設定表示", "code": "/config"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["file-settings-json"],
    },
    {
        "id": "slash-model", "name": "/model", "category": "slash-command",
        "summary_ja": "使用するモデルを切り替え",
        "description_ja": "Opus / Sonnet / Haiku など、現在のセッションで使用するモデルを切り替える。",
        "examples": [{"title": "モデル切替", "code": "/model"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-status", "name": "/status", "category": "slash-command",
        "summary_ja": "セッション状態を表示",
        "description_ja": "現在のセッションの統計情報（モデル、ディレクトリ、git状態など）を表示。",
        "examples": [{"title": "状態確認", "code": "/status"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-cost", "name": "/cost", "category": "slash-command",
        "summary_ja": "API利用コストを表示",
        "description_ja": "現在のセッションでのAPIトークン使用量とコストを確認。",
        "examples": [{"title": "コスト確認", "code": "/cost"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-compact", "name": "/compact", "category": "slash-command",
        "summary_ja": "コンテキストを強制圧縮",
        "description_ja": "コンテキストが膨らんだとき、過去の会話を要約して圧縮。重要な情報は保持。",
        "examples": [{"title": "圧縮実行", "code": "/compact"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-context", "hook-precompact"],
    },
    {
        "id": "slash-resume", "name": "/resume", "category": "slash-command",
        "summary_ja": "前回のセッションを再開",
        "description_ja": "終了したセッションを再開して続きから作業を再開。",
        "examples": [{"title": "再開", "code": "/resume"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["cli-resume"],
    },
    {
        "id": "slash-security-review", "name": "/security-review", "category": "slash-command",
        "summary_ja": "セキュリティレビューを実施",
        "description_ja": "現在のブランチの変更内容に対してセキュリティ観点のレビューを実行。",
        "examples": [{"title": "セキュリティ確認", "code": "/security-review"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-review"],
    },
    {
        "id": "slash-plugin", "name": "/plugin", "category": "slash-command",
        "summary_ja": "プラグインを管理",
        "description_ja": "プラグインのインストール・アンインストール・更新・一覧表示・エラー確認を行う。Marketplace からのインストールや --plugin-dir で読み込んだプラグインの管理に使う。",
        "examples": [
            {"title": "プラグイン一覧", "code": "/plugin"},
            {"title": "プラグイン更新", "code": "/plugin update"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-reload-plugins", "slash-doctor"],
    },
    {
        "id": "slash-skills", "name": "/skills", "category": "slash-command",
        "summary_ja": "利用可能なスキルを一覧・検索",
        "description_ja": "インストール済みのスキルを一覧表示。テキスト入力でフィルタリング可能。スキルを選択するとプロンプトに `/skill-name` が補完される。",
        "examples": [
            {"title": "スキル一覧", "code": "/skills"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["skill-overview", "slash-plugin"],
    },
    {
        "id": "slash-mcp", "name": "/mcp", "category": "slash-command",
        "summary_ja": "MCPサーバーの接続状態を確認",
        "description_ja": "接続中の MCP サーバー一覧・ツール数・認証状態を表示。0ツールのサーバーはフラグ表示される。重複URLサーバーの警告も表示。",
        "examples": [
            {"title": "MCP状態確認", "code": "/mcp"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["mcp-overview", "file-mcp-json"],
    },
    {
        "id": "slash-doctor", "name": "/doctor", "category": "slash-command",
        "summary_ja": "環境の診断・問題チェック",
        "description_ja": "MCP サーバーのエラー、無効化されたプラグインの警告、バージョン競合などの問題を診断して表示。トラブルシュートの第一歩。",
        "examples": [
            {"title": "診断実行", "code": "/doctor"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-plugin", "slash-mcp"],
    },
    {
        "id": "slash-usage", "name": "/usage", "category": "slash-command",
        "summary_ja": "トークン使用量とコストを確認",
        "description_ja": "現在セッションおよび過去の API トークン使用量・コストを表示。/cost と /stats のタブも /usage 内から開ける（v2.1.118 で統合）。",
        "examples": [
            {"title": "使用量確認", "code": "/usage"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-cost"],
    },
    {
        "id": "slash-effort", "name": "/effort", "category": "slash-command",
        "summary_ja": "Thinking の処理強度を調整",
        "description_ja": "Claude の思考量（effort）を low / normal / high / max / auto から選択。Opus モデルの xhigh も設定可能。速度と精度のトレードオフを制御。",
        "examples": [
            {"title": "最大思考量", "code": "/effort max"},
            {"title": "自動調整", "code": "/effort auto"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-model"],
    },
    {
        "id": "slash-rename", "name": "/rename", "category": "slash-command",
        "summary_ja": "セッションに名前をつける",
        "description_ja": "現在のセッションにわかりやすい名前を付ける。ステータスバーに表示され、/resume での再開時に識別しやすくなる。",
        "examples": [
            {"title": "名前を設定", "code": "/rename 認証機能の実装"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-resume"],
    },
    {
        "id": "slash-login", "name": "/login", "category": "slash-command",
        "summary_ja": "OAuth 認証を再実行",
        "description_ja": "トークン期限切れ・認証エラー時に OAuth ログインを再実行。CLAUDE_CODE_OAUTH_TOKEN 環境変数が設定されていてもディスク認証に切り替えられる。",
        "examples": [
            {"title": "ログイン", "code": "/login"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-permissions", "name": "/permissions", "category": "slash-command",
        "summary_ja": "許可・拒否されたコマンドを管理",
        "description_ja": "Auto モードで拒否されたコマンドの履歴を確認・リトライ。許可ルールの追加・削除も可能。Recent タブで直近の許可状況を確認。",
        "examples": [
            {"title": "許可状態確認", "code": "/permissions"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["mode-permission"],
    },
    {
        "id": "slash-add-dir", "name": "/add-dir", "category": "slash-command",
        "summary_ja": "作業ディレクトリを追加",
        "description_ja": "現在のセッションに追加のディレクトリを読み込む。--remember オプションで永続化可能。複数リポジトリにまたがる作業に便利。",
        "examples": [
            {"title": "ディレクトリ追加", "code": "/add-dir ../other-repo"},
            {"title": "永続追加", "code": "/add-dir --remember ../shared-lib"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-branch", "name": "/branch", "category": "slash-command",
        "summary_ja": "セッションをブランチ（分岐）する",
        "description_ja": "現在のセッションをフォークして別の方向を試す。分岐したセッションは /resume で再開可能。実験的な変更を本流に影響させずに試すのに使う。",
        "examples": [
            {"title": "セッション分岐", "code": "/branch"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-resume"],
    },
    {
        "id": "slash-copy", "name": "/copy", "category": "slash-command",
        "summary_ja": "最後の応答をクリップボードにコピー",
        "description_ja": "Claude の直前の応答をクリップボードにコピー。マークダウン形式で GitHub・Notion・Slack に貼り付けるのに最適。tmux 環境でも動作（/terminal-setup 要設定）。",
        "examples": [
            {"title": "全文コピー", "code": "/copy"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-terminal-setup"],
    },
    {
        "id": "slash-remote-control", "name": "/remote-control", "category": "slash-command",
        "summary_ja": "ブラウザ・スマホからセッションを継続",
        "description_ja": "CLI セッションを claude.ai/code に接続し、ブラウザやスマートフォンから作業を引き継げる。Remote Control 接続中はセッションカラーも同期される。",
        "examples": [
            {"title": "リモート接続", "code": "/remote-control"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-terminal-setup", "name": "/terminal-setup", "category": "slash-command",
        "summary_ja": "ターミナル環境を最適化",
        "description_ja": "Claude Code が最適動作するようターミナルを設定。iTerm2 のクリップボードアクセス許可・スクロール感度調整などを自動設定する。",
        "examples": [
            {"title": "ターミナル設定", "code": "/terminal-setup"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-copy"],
    },
    {
        "id": "slash-reload-plugins", "name": "/reload-plugins", "category": "slash-command",
        "summary_ja": "プラグインをリロード",
        "description_ja": "インストール済みプラグインを再読み込み。プラグインを編集・更新した後に変更を即反映させる。依存パッケージの自動インストールも行う。",
        "examples": [
            {"title": "プラグイン再読込", "code": "/reload-plugins"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-plugin"],
    },
    {
        "id": "slash-color", "name": "/color", "category": "slash-command",
        "summary_ja": "セッションのアクセントカラーを設定",
        "description_ja": "現在のセッションのUI色を変更。引数なしで実行するとランダムに選択。Remote Control 接続時は claude.ai/code にも同期される。",
        "examples": [
            {"title": "ランダム色", "code": "/color"},
            {"title": "色を指定", "code": "/color blue"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-remote-control"],
    },
    {
        "id": "slash-loop", "name": "/loop", "category": "slash-command",
        "summary_ja": "プロンプトを定期実行スケジュール",
        "description_ja": "指定した間隔でプロンプトやスラッシュコマンドを繰り返し実行。/loop 5m デプロイ確認 のように使う。Esc でキャンセル可能。`/proactive` はエイリアス（v2.1.105）。Bedrock/Vertex でも利用可。",
        "examples": [
            {"title": "5分ごとにデプロイ確認", "code": "/loop 5m デプロイ状態を確認して"},
            {"title": "スラッシュコマンドを定期実行", "code": "/loop 10m /review"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-compact"],
    },
    {
        "id": "slash-theme", "name": "/theme", "category": "slash-command",
        "summary_ja": "UIテーマを切り替え・カスタマイズ",
        "description_ja": "テーマピッカーを開きビルトインテーマを選択、または ~/.claude/themes/ のJSONファイルで独自テーマを作成。Auto(match terminal)でダーク/ライト自動切替も可。Ctrl+t でシンタックスハイライトをON/OFF。",
        "examples": [
            {"title": "テーマ切替", "code": "/theme"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-config"],
    },
    {
        "id": "slash-stats", "name": "/stats", "category": "slash-command",
        "summary_ja": "APIトークン使用統計を表示",
        "description_ja": "お気に入りモデル・使用量グラフ・使用ストリーク等の詳細統計を表示。v2.1.118 以降は /usage の Stats タブへのショートカットとして動作。r キーで Last 7 days / Last 30 days / All time を切替。",
        "examples": [
            {"title": "統計表示", "code": "/stats"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-usage", "slash-cost"],
    },
    {
        "id": "slash-feedback", "name": "/feedback", "category": "slash-command",
        "summary_ja": "フィードバックをAnthropicに送信",
        "description_ja": "バグ報告・機能要望をAnthropicに直接送信し、GitHub issue URL も生成。認証状態によって利用不可の場合はメニューにその旨が表示される。長い説明文も正しく処理される（v2.1.14 修正済）。",
        "examples": [
            {"title": "フィードバック送信", "code": "/feedback"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-voice", "name": "/voice", "category": "slash-command",
        "summary_ja": "音声入力（ボイスモード）を切替",
        "description_ja": "音声でプロンプトを入力するボイスモードをON/OFF。有効化時に認識言語を表示し、未対応言語は警告。Remote Control セッションでも動作。認証プランによっては非表示になる。",
        "examples": [
            {"title": "音声入力ON", "code": "/voice"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-tui", "name": "/tui", "category": "slash-command",
        "summary_ja": "フリッカーフリーなフルスクリーンレンダラーに切替",
        "description_ja": "/tui fullscreen で代替レンダラーに切り替える。フリッカーなし・低メモリ使用量・マウスサポート・選択時の自動コピーを備える。worktree内セッションでも利用可能。",
        "examples": [
            {"title": "フルスクリーン切替", "code": "/tui fullscreen"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-extra-usage", "name": "/extra-usage", "category": "slash-command",
        "summary_ja": "追加API利用を有効化するダイアログを開く",
        "description_ja": "プランの使用量上限を超えた追加API利用を有効化する。有効化後は /fast が即座に使用可能になる。VS Code および Remote Control（ブラウザ・スマホ）からも利用可能。",
        "examples": [
            {"title": "追加利用設定", "code": "/extra-usage"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-usage", "slash-upgrade"],
    },
    {
        "id": "slash-rewind", "name": "/rewind", "category": "slash-command",
        "summary_ja": "会話を巻き戻してコード変更を取り消す",
        "description_ja": "ピッカーで任意のポイントを選択して会話を巻き戻し、コード変更も元に戻せる。/undo はエイリアス。VS Code では Esc×2 でも起動可能。",
        "examples": [
            {"title": "巻き戻しピッカー", "code": "/rewind"},
            {"title": "エイリアス", "code": "/undo"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-upgrade", "name": "/upgrade", "category": "slash-command",
        "summary_ja": "Claude Maxプランへスムーズにアップグレード",
        "description_ja": "Claude Max プランへの切り替えダイアログを開く。現在の認証設定で利用できない場合は自動的に非表示になる。レート制限時にサジェストされる場合がある。",
        "examples": [
            {"title": "プランアップグレード", "code": "/upgrade"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-extra-usage"],
    },
    {
        "id": "slash-exit", "name": "/exit", "category": "slash-command",
        "summary_ja": "セッションを終了してアーカイブ",
        "description_ja": "現在のセッションを終了しアーカイブする。Remote Control（ブラウザ・スマホ）からも実行可能。終了時にセッションが確実に保存される。",
        "examples": [
            {"title": "セッション終了", "code": "/exit"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-resume"],
    },
    {
        "id": "slash-export", "name": "/export", "category": "slash-command",
        "summary_ja": "会話をファイルにエクスポート",
        "description_ja": "現在の会話を外部ファイルに書き出す。絶対パスや ~ も指定可能で、完了後にファイルの全パスを表示。会話の共有や記録保存に使う。",
        "examples": [
            {"title": "デフォルト出力", "code": "/export"},
            {"title": "パス指定", "code": "/export ~/my-session.txt"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-copy", "slash-resume"],
    },
    {
        "id": "slash-ultrareview", "name": "/ultrareview", "category": "slash-command",
        "summary_ja": "クラウドで並列マルチエージェントコードレビュー",
        "description_ja": "クラウド上でマルチエージェントを並列実行し包括的なコードレビューを行う。引数なしで現在ブランチをレビュー、`/ultrareview <PR番号>` でGitHub PRを対象指定。`claude ultrareview` でCIからの非対話実行も可。",
        "examples": [
            {"title": "現在ブランチをレビュー", "code": "/ultrareview"},
            {"title": "特定PRをレビュー", "code": "/ultrareview 123"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-review", "slash-security-review"],
    },
    {
        "id": "slash-plan", "name": "/plan", "category": "slash-command",
        "summary_ja": "プランモードをプロンプトから直接起動",
        "description_ja": "プランモード（読み取り専用計画モード）をスラッシュコマンドで直接有効化する。説明文を引数に渡すと `/plan 認証バグを修正` のように即座に計画を開始できる。Shift+Tab でも同様に切り替え可能。",
        "examples": [
            {"title": "プランモード開始", "code": "/plan"},
            {"title": "説明付きで開始", "code": "/plan 認証バグを修正する"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["mode-plan", "agent-plan"],
    },
    {
        "id": "slash-tasks", "name": "/tasks", "category": "slash-command",
        "summary_ja": "バックグラウンドタスクの状態を管理・確認",
        "description_ja": "バックグラウンドで実行中のタスクの状態を確認・管理するダイアログを開く。タスクが1つのみの場合は直接タスク詳細に遷移する。remote session URL なども確認できる。",
        "examples": [
            {"title": "タスク一覧", "code": "/tasks"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["tool-todowrite", "slash-agents"],
    },
    {
        "id": "slash-btw", "name": "/btw", "category": "slash-command",
        "summary_ja": "応答生成中にサイドクエスチョンを割り込ませる",
        "description_ja": "Claudeが応答を生成中に `/btw 質問` と入力してサイドの質問を差し込める。貼り付けたテキストも含めて処理され、メインの応答を中断せずに別の問いを解決できる。",
        "examples": [
            {"title": "サイドクエスチョン", "code": "/btw この関数の引数の型は？"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "slash-insights", "name": "/insights", "category": "slash-command",
        "summary_ja": "セッション履歴からインサイトレポートを生成",
        "description_ja": "現在のセッション履歴を分析してインサイトレポートを生成し、レポートファイルへのリンクを返す。ツール呼び出し履歴も含めて処理される。セッションの振り返りや記録保存に使う。",
        "examples": [
            {"title": "インサイト生成", "code": "/insights"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-stats", "slash-usage"],
    },
    {
        "id": "slash-release-notes", "name": "/release-notes", "category": "slash-command",
        "summary_ja": "Claude Codeのリリースノートを確認",
        "description_ja": "Claude Code の過去バージョンのリリースノートをインタラクティブなバージョンピッカーで閲覧できる（v2.1.92以降）。最新版から任意バージョンを選択して更新内容を確認。",
        "examples": [
            {"title": "リリースノート表示", "code": "/release-notes"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-keybindings", "name": "/keybindings", "category": "slash-command",
        "summary_ja": "カスタムキーバインド設定を開始",
        "description_ja": "カスタムキーボードショートカットの設定ガイドを表示。コンテキストごとのキーバインド設定・コードシーケンス作成・~/.claude/keybindings.json の編集方法を案内する（v2.1.18で追加）。",
        "examples": [
            {"title": "キーバインド設定開始", "code": "/keybindings"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["misc-keybindings"],
    },
    {
        "id": "slash-sandbox", "name": "/sandbox", "category": "slash-command",
        "summary_ja": "サンドボックス実行環境を管理",
        "description_ja": "サンドボックス環境の状態を確認するタブ付きダイアログを表示。Dependencies タブで依存関係のインストール状況と手順を確認できる。Tab/矢印キーでタブ切替が可能。",
        "examples": [
            {"title": "サンドボックス確認", "code": "/sandbox"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "slash-claude-api", "name": "/claude-api", "category": "slash-command",
        "summary_ja": "Claude API開発を支援するスキルを起動",
        "description_ja": "Claude API・Anthropic SDK を使ったアプリ開発を支援するスキル（v2.1.69で追加）。Managed Agents、エージェント設計パターン、ツール設計・コンテキスト管理・キャッシング戦略のガイダンスを提供。",
        "examples": [
            {"title": "スキル起動", "code": "/claude-api"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["skill-overview"],
    },
    {
        "id": "slash-debug", "name": "/debug", "category": "slash-command",
        "summary_ja": "デバッグログをセッション中に切り替え",
        "description_ja": "現在のセッションのデバッグログをミッドセッションで切替（v2.1.30追加・v2.1.71更新）。デフォルトでは記録されないデバッグログをオンにしてトラブルシュートに使う。Claudeによるセッション診断にも対応。",
        "examples": [
            {"title": "デバッグ切替", "code": "/debug"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-doctor"],
    },
    {
        "id": "slash-todos", "name": "/todos", "category": "slash-command",
        "summary_ja": "現在のTODOアイテム一覧を表示",
        "description_ja": "TodoWriteツールで記録された現在のセッションのTODOアイテムをオーバーレイで一覧表示（v1.0.94で追加）。pending/in_progress/completed の進捗状態を確認できる。",
        "examples": [
            {"title": "TODO一覧表示", "code": "/todos"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-todowrite"],
    },
    {
        "id": "slash-recap", "name": "/recap", "category": "slash-command",
        "summary_ja": "セッション再開時の作業コンテキストを要約",
        "description_ja": "セッションに戻った際に直前の作業内容のコンテキストを提供するリキャップ機能（v2.1.108追加）。/config で自動表示を設定でき、テレメトリ無効時は CLAUDE_CODE_ENABLE_AWAY_SUMMARY 環境変数で強制有効化可能。",
        "examples": [
            {"title": "リキャップ表示", "code": "/recap"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-resume", "slash-compact"],
    },
    {
        "id": "slash-less-permission-prompts", "name": "/less-permission-prompts", "category": "slash-command",
        "summary_ja": "許可プロンプト削減の allowlist を自動提案",
        "description_ja": "過去のトランスクリプトをスキャンして読み取り専用のBash・MCPツール呼び出しパターンを検出し、`.claude/settings.json` の許可リストとして優先順に提案するスキル（v2.1.111で追加）。",
        "examples": [
            {"title": "許可リスト提案", "code": "/less-permission-prompts"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-permissions", "file-settings-json"],
    },
    {
        "id": "slash-setup-bedrock", "name": "/setup-bedrock", "category": "slash-command",
        "summary_ja": "Amazon Bedrock接続を対話形式でセットアップ",
        "description_ja": "Amazon Bedrock 経由でClaudeを利用するための設定を対話形式で実施（v2.1.111改善）。CLAUDE_CONFIG_DIR 設定時は実際のパスを表示し、既存ピンからモデル候補を提案、対応モデルでは1Mコンテキストオプションも提示。/setup-vertex も同様。",
        "examples": [
            {"title": "Bedrock設定", "code": "/setup-bedrock"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "slash-fast", "name": "/fast", "category": "slash-command",
        "summary_ja": "Opus 4.6の高速応答モードを切り替え",
        "description_ja": "Claude Opus 4.6 ベースの高速応答モード（Fast Mode）をON/OFFする。サードパーティプロバイダーでは利用不可で「not available」と表示される。/extra-usage 有効化後は即座に使用可能になる（v2.1.37修正）。",
        "examples": [
            {"title": "高速モード切替", "code": "/fast"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["misc-fast-mode", "slash-extra-usage"],
    },
    {
        "id": "slash-focus", "name": "/focus", "category": "slash-command",
        "summary_ja": "フルスクリーンTUIのフォーカスビューを切り替え",
        "description_ja": "フルスクリーンレンダラー（/tui fullscreen）でのフォーカスビューをON/OFFする（v2.1.110追加）。Ctrl+O はノーマル/詳細ビューの切替専用に変更され、フォーカスビューはこのコマンドで制御する。フルスクリーン無効時は有効化方法を案内。",
        "examples": [
            {"title": "フォーカス切替", "code": "/focus"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-tui"],
    },
    {
        "id": "slash-team-onboarding", "name": "/team-onboarding", "category": "slash-command",
        "summary_ja": "チームメンバー向けオンボーディングガイドを生成",
        "description_ja": "ローカルの Claude Code 使用履歴をもとに、チームメンバーのランプアップガイドを自動生成する（v2.1.101追加）。プロジェクト固有のコマンドパターンや慣習をまとめたドキュメントを作成し、新規参加者の立ち上がりを支援する。",
        "examples": [
            {"title": "ガイド生成", "code": "/team-onboarding"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["file-claude-md", "file-onboarding-md"],
    },
    {
        "id": "slash-install-github-app", "name": "/install-github-app", "category": "slash-command",
        "summary_ja": "GitHub App連携をインストール",
        "description_ja": "Claude Code と GitHub を連携する GitHub App のインストールを対話形式で実施。エラーハンドリングが強化されており（v1.0.7改善）、Esc でダイアログを閉じられる（v2.1.136修正）。GitHub Actions 連携のセットアップに使う。",
        "examples": [
            {"title": "GitHub App設定", "code": "/install-github-app"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "slash-simplify", "name": "/simplify", "category": "slash-command",
        "summary_ja": "変更コードの品質・効率をレビューして修正",
        "description_ja": "v2.1.63で追加されたバンドル型スラッシュコマンド。変更されたコードを再利用性・品質・効率の観点でレビューし、検出した問題を修正する。コードレビューと実際のリファクタを一括で行う。",
        "examples": [
            {"title": "コード簡素化・修正", "code": "/simplify"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-review"],
    },
    {
        "id": "slash-goal", "name": "/goal", "category": "slash-command",
        "summary_ja": "完了条件を設定して複数ターンを自動実行",
        "description_ja": "完了条件をClaudeに設定し、条件が満たされるまで複数ターンにわたって自動実行する（v2.1.139追加）。インタラクティブ・--print・Remote Control のすべてで動作。実行中は経過時間・ターン数・トークン数をオーバーレイパネルでリアルタイム表示。",
        "examples": [
            {"title": "完了条件付き実行", "code": "/goal テストがすべて通るまで修正を続けて"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-loop"],
    },
    {
        "id": "slash-scroll-speed", "name": "/scroll-speed", "category": "slash-command",
        "summary_ja": "マウスホイールのスクロール速度を調整",
        "description_ja": "マウスホイールのスクロール速度をリアルタイムプレビュー付きで調整するコマンド（v2.1.139追加）。カーソルや VS Code でのスクロール速度問題にも対応しており、トラックパッドとマウスホイールのスクロール量を別々に制御できる。",
        "examples": [
            {"title": "スクロール速度調整", "code": "/scroll-speed"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-tui", "slash-terminal-setup"],
    },
    {
        "id": "slash-schedule", "name": "/schedule", "category": "slash-command",
        "summary_ja": "定期スケジュールのリモートエージェントを管理",
        "description_ja": "cron スケジュールで定期実行するリモートエージェント（ルーティン）の作成・一覧・実行を管理する（v2.1.139）。claude.ai 認証が必要で、ANTHROPIC_API_KEY 設定時は Remote Control・claude.ai MCP コネクタと同様に無効化される。",
        "examples": [
            {"title": "スケジュール管理", "code": "/schedule"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-loop", "slash-remote-control"],
    },
    {
        "id": "slash-ultraplan", "name": "/ultraplan", "category": "slash-command",
        "summary_ja": "クラウドセッションで計画をリファイン",
        "description_ja": "プランモードから「Refine with Ultraplan」として起動できるクラウドベースの計画精緻化機能（v2.1.101追加）。デフォルトのクラウド環境を自動生成してリモートセッションURLをトランスクリプトに表示。組織またはAuth設定でクラウドに到達できない場合は非表示になる。",
        "examples": [
            {"title": "クラウドで計画精緻化", "code": "/ultraplan"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["mode-plan", "slash-plan"],
    },
    {
        "id": "slash-powerup", "name": "/powerup", "category": "slash-command",
        "summary_ja": "インタラクティブな機能チュートリアルを起動",
        "description_ja": "Claude Code の各機能をアニメーションデモ付きのインタラクティブなレッスン形式で学べる（v2.1.90追加）。ハンズオン形式で機能の使い方を習得できる。",
        "examples": [
            {"title": "チュートリアル起動", "code": "/powerup"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-help"],
    },
    {
        "id": "slash-teleport", "name": "/teleport", "category": "slash-command",
        "summary_ja": "リモートセッションを再開（claude.ai登録者向け）",
        "description_ja": "claude.ai 登録者向けのリモートセッション再開コマンド（v2.1.0追加）。/remote-env でリモートセッションを設定し、/teleport で再開する。Remote Control との組み合わせで利用可能。",
        "examples": [
            {"title": "リモートセッション再開", "code": "/teleport"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-remote-env", "slash-remote-control", "slash-resume"],
    },
    {
        "id": "slash-remote-env", "name": "/remote-env", "category": "slash-command",
        "summary_ja": "リモートセッション環境を設定（claude.ai登録者向け）",
        "description_ja": "claude.ai 登録者向けのリモートセッション設定コマンド（v2.1.0追加）。リモート環境のパラメータを設定し、/teleport でセッションを再開する際の接続先を定義する。",
        "examples": [
            {"title": "リモート環境設定", "code": "/remote-env"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-teleport", "slash-remote-control"],
    },
    {
        "id": "slash-bg", "name": "/bg", "category": "slash-command",
        "summary_ja": "バックグラウンドエージェントを起動",
        "description_ja": "バックグラウンドエージェントをコマンドまたはキーボードショートカット ←← で起動する。起動時に現在の権限モードを引き継ぐ（v2.1.141）。実行中のタスクは /tasks で確認可能。",
        "examples": [
            {"title": "バックグラウンド起動", "code": "/bg"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-tasks", "slash-agents"],
    },
    {
        "id": "slash-setup-vertex", "name": "/setup-vertex", "category": "slash-command",
        "summary_ja": "Google Vertex AI接続を対話形式でセットアップ",
        "description_ja": "Google Cloud Vertex AI 経由でClaudeを利用するための設定を対話形式で実施（v2.1.111改善）。CLAUDE_CONFIG_DIR 設定時は実際のパスを表示し、既存ピンからモデル候補を提案、対応モデルでは1Mコンテキストオプションも提示。",
        "examples": [
            {"title": "Vertex AI設定", "code": "/setup-vertex"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-setup-bedrock"],
    },
    {
        "id": "slash-chrome", "name": "/chrome", "category": "slash-command",
        "summary_ja": "ブラウザをClaudeから直接操作（Beta）",
        "description_ja": "Claude in Chrome拡張機能（claude.ai/chrome）と連携し、ブラウザを直接Claude Codeから操作できるベータ機能（v2.0.72追加）。認証設定によっては非表示になる場合がある。",
        "examples": [
            {"title": "Chrome連携", "code": "/chrome"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "slash-commit-push-pr", "name": "/commit-push-pr", "category": "slash-command",
        "summary_ja": "コミット・プッシュ・PR作成を一括実行",
        "description_ja": "git commit・push・PR作成を一括実行するバンドルスキル。MCP経由でSlackが設定されている場合はPR URLを自動的にSlackチャンネルに投稿する（v2.1.20で変更）。",
        "examples": [
            {"title": "コミット+プッシュ+PR作成", "code": "/commit-push-pr"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-simplify", "slash-review"],
    },
    {
        "id": "slash-web-setup", "name": "/web-setup", "category": "slash-command",
        "summary_ja": "GitHub App Web接続をセットアップ",
        "description_ja": "Claude Code とGitHub AppのWeb接続を設定するダイアログ（v2.1.136追加）。既存の接続を上書きする前に警告を表示する（v2.1.142）。Escキーでダイアログを閉じられる。",
        "examples": [
            {"title": "Web接続設定", "code": "/web-setup"},
        ],
        "links": [], "difficulty": 2, "tier": "free", "related": ["slash-install-github-app"],
    },
    {
        "id": "slash-update", "name": "/update", "category": "slash-command",
        "summary_ja": "Claude Codeをセッション内から最新版に更新",
        "description_ja": "セッション内から Claude Code を最新バージョンに更新するコマンド。`claude update` CLI サブコマンドと同等の更新を対話セッションから実行可能。worktree 内セッションでも動作（v2.1.116 修正）。`DISABLE_UPDATES` 環境変数で全更新パスを無効化可能。",
        "examples": [
            {"title": "更新実行", "code": "/update"},
        ],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "slash-fork", "name": "/fork", "category": "slash-command",
        "summary_ja": "/branch の旧コマンド名（エイリアス）",
        "description_ja": "v2.1.77 で `/branch` にリネームされた旧コマンド名。エイリアスとして引き続き動作し、セッションをフォークして別の方向を試すことができる。分岐したセッションは /resume で再開可能。新しい記法では `/branch` を使用することを推奨。",
        "examples": [
            {"title": "セッション分岐（旧コマンド）", "code": "/fork"},
        ],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-branch"],
    },

    # ========== Built-in Tools ==========
    {
        "id": "tool-bash", "name": "Bash", "category": "tool",
        "summary_ja": "シェルコマンドを実行",
        "description_ja": "シェル環境でコマンドを実行。npm install、git操作、ビルドコマンドなどに使う。最大10分のタイムアウト指定可能。",
        "examples": [{"title": "git status実行", "code": "Bash: git status"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "tool-read", "name": "Read", "category": "tool",
        "summary_ja": "ファイルを読み取り",
        "description_ja": "ファイルの内容を読み取る。テキスト、PDF、画像、Jupyter notebookに対応。行番号付き、オフセット指定可能。",
        "examples": [{"title": "ファイル読込", "code": "Read: /path/to/file.ts"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-write", "tool-edit"],
    },
    {
        "id": "tool-write", "name": "Write", "category": "tool",
        "summary_ja": "新規ファイルを作成",
        "description_ja": "ローカルファイルシステムにファイルを作成・上書き。既存ファイルは事前に Read 必須。",
        "examples": [{"title": "新規作成", "code": "Write: 新ファイルを書き出す"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-read", "tool-edit"],
    },
    {
        "id": "tool-edit", "name": "Edit", "category": "tool",
        "summary_ja": "既存ファイルを部分編集",
        "description_ja": "old_string と new_string を指定して文字列置換。差分のみ送信できるので Write より効率的。",
        "examples": [{"title": "文字列置換", "code": "Edit: old_string → new_string"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["tool-multiedit", "tool-write"],
    },
    {
        "id": "tool-multiedit", "name": "MultiEdit", "category": "tool",
        "summary_ja": "1ファイルに複数編集を一括適用",
        "description_ja": "複数の Edit 操作を同時にトランザクションで適用。1つでも失敗すると全てロールバック。",
        "examples": [{"title": "複数編集", "code": "MultiEdit: 編集A,編集B,編集C"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["tool-edit"],
    },
    {
        "id": "tool-glob", "name": "Glob", "category": "tool",
        "summary_ja": "パターンでファイル検索",
        "description_ja": "ワイルドカードパターン（src/**/*.ts等）でファイルを高速検索。",
        "examples": [{"title": "TS検索", "code": "Glob: src/**/*.ts"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-grep"],
    },
    {
        "id": "tool-grep", "name": "Grep", "category": "tool",
        "summary_ja": "ファイル内容を全文検索",
        "description_ja": "ripgrepベースの高速検索。正規表現対応、コンテキスト行表示、ファイル種別フィルタなど多機能。",
        "examples": [{"title": "関数定義検索", "code": "Grep: \"function login\""}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["tool-glob"],
    },
    {
        "id": "tool-task", "name": "Task (Agent)", "category": "tool",
        "summary_ja": "サブエージェントを起動",
        "description_ja": "別のエージェントを起動して並列タスク実行。Explore/Plan/general-purpose 等の組み込みエージェントを使える。",
        "examples": [{"title": "サブエージェント起動", "code": "Task: subagent_type=Explore"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["agent-subagent", "agent-explore", "agent-plan"],
    },
    {
        "id": "tool-websearch", "name": "WebSearch", "category": "tool",
        "summary_ja": "Webを検索",
        "description_ja": "最新情報を検索。日付・ドメインフィルタ対応。米国限定。",
        "examples": [{"title": "最新情報検索", "code": "WebSearch: \"Claude Code 2026\""}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-webfetch"],
    },
    {
        "id": "tool-webfetch", "name": "WebFetch", "category": "tool",
        "summary_ja": "URLを取得して要約",
        "description_ja": "指定URLからHTML取得→マークダウン変換→AIが要約。15分キャッシュあり。",
        "examples": [{"title": "ドキュメント取得", "code": "WebFetch: docs.anthropic.com/..."}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["tool-websearch"],
    },
    {
        "id": "tool-notebookedit", "name": "NotebookEdit", "category": "tool",
        "summary_ja": "Jupyter Notebookセルを編集",
        "description_ja": ".ipynb ファイルの特定セルを編集・追加・削除。データサイエンス作業向け。",
        "examples": [{"title": "セル編集", "code": "NotebookEdit: cell_id=...,new_source=..."}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["tool-edit"],
    },
    {
        "id": "tool-todowrite", "name": "TodoWrite", "category": "tool",
        "summary_ja": "タスクリストで進捗管理",
        "description_ja": "現在のセッション内のタスク追跡。pending/in_progress/completed の3状態。複雑な作業の整理に。",
        "examples": [{"title": "タスク追加", "code": "TodoWrite: 認証実装、テスト追加"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "tool-slashcommand", "name": "SlashCommand", "category": "tool",
        "summary_ja": "別のスラッシュコマンドを実行",
        "description_ja": "Claude が他のスラッシュコマンドを呼び出す内部ツール。コマンド連携の基盤。",
        "examples": [{"title": "コマンド呼出", "code": "SlashCommand: /init"}],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },

    # ========== Hooks ==========
    {
        "id": "hook-pretooluse", "name": "PreToolUse Hook", "category": "hook",
        "summary_ja": "ツール実行前のフック",
        "description_ja": "ツール実行直前に走るフック。matcher で対象ツール指定、危険コマンドのブロックや事前検証に使える。",
        "examples": [{"title": "rm -rf ブロック", "code": "matcher: \"Bash\", action: block on rm -rf"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["hook-posttooluse", "slash-hooks"],
    },
    {
        "id": "hook-posttooluse", "name": "PostToolUse Hook", "category": "hook",
        "summary_ja": "ツール実行後のフック",
        "description_ja": "ツール実行直後に走るフック。ログ記録、自動フォーマット、テスト実行などに使う。",
        "examples": [{"title": "編集後にprettier", "code": "matcher: Edit/Write -> npx prettier"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["hook-pretooluse"],
    },
    {
        "id": "hook-stop", "name": "Stop Hook", "category": "hook",
        "summary_ja": "Claude応答完了時のフック",
        "description_ja": "Claudeの応答が終了したときに走るフック。完了通知やセッションログ出力に。",
        "examples": [{"title": "通知音", "code": "Stop: afplay /sound.wav"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["hook-subagentstop"],
    },
    {
        "id": "hook-subagentstop", "name": "SubagentStop Hook", "category": "hook",
        "summary_ja": "サブエージェント完了時のフック",
        "description_ja": "サブエージェント（Task tool）が完了したときに走るフック。",
        "examples": [{"title": "サブエージェント完了通知", "code": "SubagentStop: log to file"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["hook-stop"],
    },
    {
        "id": "hook-sessionstart", "name": "SessionStart Hook", "category": "hook",
        "summary_ja": "セッション開始時のフック",
        "description_ja": "Claude Code セッション開始時に走るフック。git pull や初期メッセージ表示に。",
        "examples": [{"title": "git pull", "code": "SessionStart: git pull"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["hook-sessionend"],
    },
    {
        "id": "hook-sessionend", "name": "SessionEnd Hook", "category": "hook",
        "summary_ja": "セッション終了時のフック",
        "description_ja": "セッション終了時に走るフック。コミット忘れ警告、サマリー出力など。",
        "examples": [{"title": "未コミット警告", "code": "SessionEnd: git status check"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["hook-sessionstart"],
    },
    {
        "id": "hook-userpromptsubmit", "name": "UserPromptSubmit Hook", "category": "hook",
        "summary_ja": "ユーザー入力送信時のフック",
        "description_ja": "ユーザーがプロンプトを送信した直後に走る。入力内容を加工・追記したり、追加コンテキスト注入に使える。",
        "examples": [{"title": "翻訳指示自動追加", "code": "UserPromptSubmit: 日本語入力に英訳ヒント追加"}],
        "links": [], "difficulty": 4, "tier": "free", "related": [],
    },
    {
        "id": "hook-precompact", "name": "PreCompact Hook", "category": "hook",
        "summary_ja": "コンテキスト圧縮直前のフック",
        "description_ja": "コンテキスト圧縮が走る直前に呼ばれる。圧縮前に重要な情報を保存したい時に。",
        "examples": [{"title": "圧縮前のスナップショット", "code": "PreCompact: dump to file"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["slash-compact"],
    },
    {
        "id": "hook-notification", "name": "Notification Hook", "category": "hook",
        "summary_ja": "通知イベントのフック",
        "description_ja": "Claudeが通知を出すタイミング（権限要求等）で走るフック。デスクトップ通知連携などに。",
        "examples": [{"title": "macOS通知", "code": "Notification: osascript display notification"}],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },

    # ========== Modes ==========
    {
        "id": "mode-plan", "name": "Plan Mode", "category": "mode",
        "summary_ja": "読み取り専用の計画モード",
        "description_ja": "Shift+Tabで切替。コードを書かずに「これからやること」を提案するだけ。実装前のレビューに最適。",
        "examples": [{"title": "切替", "code": "Shift + Tab"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["agent-plan"],
    },
    {
        "id": "mode-permission", "name": "Permission Modes", "category": "mode",
        "summary_ja": "ツール実行時の確認制御",
        "description_ja": "default(都度確認)、acceptEdits(編集自動)、bypassPermissions(全自動)、plan(読取のみ)の4モード。",
        "examples": [{"title": "自動編集モード", "code": "permissionMode: acceptEdits"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["mode-plan"],
    },
    {
        "id": "mode-output-style", "name": "Output Styles", "category": "mode",
        "summary_ja": "応答スタイルのカスタマイズ",
        "description_ja": "Claudeの応答口調・形式を調整。簡潔モード、教育モードなどプリセットあり。",
        "examples": [{"title": "切替", "code": "/output-style"}],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },
    {
        "id": "mode-headless", "name": "Headless Mode (--print)", "category": "mode",
        "summary_ja": "対話なしで一発実行",
        "description_ja": "--print フラグで対話UIなしに1回だけプロンプトを実行して結果を返す。CIやスクリプト統合に。",
        "examples": [{"title": "ヘッドレス実行", "code": "claude --print \"PRレビューして\""}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["cli-print"],
    },

    # ========== Files & Memory ==========
    {
        "id": "file-claude-md", "name": "CLAUDE.md", "category": "file",
        "summary_ja": "プロジェクトガイダンスファイル",
        "description_ja": "リポジトリ直下に置くと Claude が自動的に読み込むプロジェクトガイダンス。コーディング規約、ディレクトリ構造、注意事項などを書く。",
        "examples": [{"title": "雛形生成", "code": "/init"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-init", "file-agents-md"],
    },
    {
        "id": "file-agents-md", "name": "AGENTS.md", "category": "file",
        "summary_ja": "エージェント定義ファイル",
        "description_ja": "サブエージェントの挙動を定義。CLAUDE.md と並列で機能する場合あり。",
        "examples": [{"title": "ファイル配置", "code": "プロジェクトルートに配置"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["file-claude-md"],
    },
    {
        "id": "file-onboarding-md", "name": "ONBOARDING.md", "category": "file",
        "summary_ja": "新規参加者向けガイド",
        "description_ja": "プロジェクトに初めて触れる人のためのオンボーディング情報。Claude が読み込んでアシストに使う。",
        "examples": [{"title": "ファイル配置", "code": "プロジェクトルートに配置"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["file-claude-md"],
    },
    {
        "id": "file-settings-json", "name": "settings.json", "category": "file",
        "summary_ja": "ユーザー全体の設定ファイル",
        "description_ja": "~/.claude/settings.json でグローバル設定。テーマ、フック、許可リスト、環境変数など。",
        "examples": [{"title": "場所", "code": "~/.claude/settings.json"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["file-settings-local-json", "slash-config"],
    },
    {
        "id": "file-settings-local-json", "name": "settings.local.json", "category": "file",
        "summary_ja": "プロジェクト固有設定",
        "description_ja": ".claude/settings.local.json でプロジェクト単位設定。git管理外、個人の許可設定などに。",
        "examples": [{"title": "場所", "code": ".claude/settings.local.json"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["file-settings-json"],
    },
    {
        "id": "file-mcp-json", "name": ".mcp.json", "category": "file",
        "summary_ja": "MCPサーバー設定ファイル",
        "description_ja": "プロジェクトに紐づく MCP サーバーを定義。stdio/SSE/HTTP の各種MCPサーバーを登録できる。",
        "examples": [{"title": "場所", "code": ".mcp.json"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["mcp-overview"],
    },
    {
        "id": "file-memory", "name": "Memory System", "category": "file",
        "summary_ja": "永続メモリシステム",
        "description_ja": "~/.claude/projects/<hash>/memory/ にユーザー嗜好・プロジェクト情報を蓄積。MEMORY.md がインデックス。",
        "examples": [{"title": "場所", "code": "~/.claude/projects/.../memory/"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["slash-memory"],
    },
    {
        "id": "file-mention", "name": "@-mentions", "category": "file",
        "summary_ja": "ファイルを@で参照",
        "description_ja": "プロンプト内で @path/to/file と書くと、そのファイルが自動的にコンテキストに追加される。",
        "examples": [{"title": "ファイル参照", "code": "@src/index.ts のバグを直して"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },

    # ========== CLI Flags ==========
    {
        "id": "cli-continue", "name": "--continue (-c)", "category": "cli",
        "summary_ja": "前回のセッションを継続",
        "description_ja": "claude --continue で直前のセッションをそのまま再開。コンテキストを失わずに続けられる。",
        "examples": [{"title": "継続実行", "code": "claude -c"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["cli-resume", "slash-resume"],
    },
    {
        "id": "cli-resume", "name": "--resume (-r)", "category": "cli",
        "summary_ja": "特定セッションを再開",
        "description_ja": "claude --resume <session-id> で過去の任意セッションを再開。",
        "examples": [{"title": "セッション選択再開", "code": "claude -r"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["cli-continue"],
    },
    {
        "id": "cli-print", "name": "--print (-p)", "category": "cli",
        "summary_ja": "ヘッドレスモードで一発実行",
        "description_ja": "対話UIを起動せずプロンプトを実行して結果を出力。スクリプト連携に。",
        "examples": [{"title": "ヘッドレス", "code": "claude -p \"PR要約して\""}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["mode-headless"],
    },
    {
        "id": "cli-model", "name": "--model", "category": "cli",
        "summary_ja": "使用モデルを起動時に指定",
        "description_ja": "claude --model claude-opus-4-7 のように、起動時に使用モデルを固定。",
        "examples": [{"title": "Opus指定起動", "code": "claude --model claude-opus-4-7"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-model"],
    },
    {
        "id": "cli-add-dir", "name": "--add-dir", "category": "cli",
        "summary_ja": "追加の作業ディレクトリを指定",
        "description_ja": "Claude のアクセスを通常のcwd以外にも広げる。複数リポジトリを横断する作業に。",
        "examples": [{"title": "別リポ追加", "code": "claude --add-dir ../other-repo"}],
        "links": [], "difficulty": 2, "tier": "free", "related": [],
    },

    # ========== Subagents ==========
    {
        "id": "agent-subagent", "name": "Subagent System", "category": "agent",
        "summary_ja": "サブエージェントの仕組み",
        "description_ja": "メインのClaudeとは別の文脈で動く専門エージェント。Task tool 経由で起動。複雑タスクの並列処理や文脈分離に。",
        "examples": [{"title": "起動例", "code": "Task: subagent_type=Explore"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["tool-task", "slash-agents"],
    },
    {
        "id": "agent-explore", "name": "Explore Agent", "category": "agent",
        "summary_ja": "高速読み取り検索エージェント",
        "description_ja": "コードを探すための読み取り専用検索エージェント。パターン・キーワード・シンボル検索に最適。並列実行で本体の文脈を消費しない。",
        "examples": [{"title": "コンポーネント検索", "code": "Task: subagent_type=Explore で\"src/components/**/*.tsx\"検索"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["agent-subagent", "tool-glob"],
    },
    {
        "id": "agent-plan", "name": "Plan Agent", "category": "agent",
        "summary_ja": "実装計画を設計するエージェント",
        "description_ja": "タスクの実装戦略を設計。ステップバイステップ計画、重要ファイル特定、アーキテクチャトレードオフ考慮。",
        "examples": [{"title": "新機能計画", "code": "Task: subagent_type=Plan で認証機能の実装計画"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["agent-subagent", "mode-plan"],
    },
    {
        "id": "agent-general-purpose", "name": "general-purpose Agent", "category": "agent",
        "summary_ja": "汎用エージェント",
        "description_ja": "特化していない汎用エージェント。複雑な調査やマルチステップタスクに使える。",
        "examples": [{"title": "汎用調査", "code": "Task: subagent_type=general-purpose"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["agent-subagent"],
    },
    {
        "id": "agent-custom", "name": "Custom Subagents", "category": "agent",
        "summary_ja": "独自サブエージェントの作成",
        "description_ja": ".claude/agents/<name>.md にエージェント定義を置くと、自分専用のサブエージェントが作れる。",
        "examples": [{"title": "ファイル配置", "code": ".claude/agents/my-agent.md"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["agent-subagent"],
    },
    {
        "id": "agent-isolation", "name": "Worktree Isolation", "category": "agent",
        "summary_ja": "git worktreeでエージェント隔離",
        "description_ja": "サブエージェントを別のgit worktreeで動かしてmainと隔離。並列開発の事故防止に。",
        "examples": [{"title": "隔離起動", "code": "Task: isolation=worktree"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["agent-subagent"],
    },

    # ========== Skills ==========
    {
        "id": "skill-overview", "name": "Skills System", "category": "skill",
        "summary_ja": "再利用可能なスキルシステム",
        "description_ja": ".claude/skills/<name>/SKILL.md でスキル定義。description のキーワードでトリガーされ、Claudeが自動的に呼び出す。",
        "examples": [{"title": "ファイル配置", "code": ".claude/skills/my-skill/SKILL.md"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["skill-structure"],
    },
    {
        "id": "skill-structure", "name": "SKILL.md Structure", "category": "skill",
        "summary_ja": "スキル定義ファイルの構造",
        "description_ja": "frontmatter に description（トリガー文）、name、tools などを書く。本文は手順・ルール・テンプレート。",
        "examples": [{"title": "雛形", "code": "---\\nname: my-skill\\ndescription: ...\\n---"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["skill-overview"],
    },
    {
        "id": "skill-marketplace", "name": "Plugin Marketplace", "category": "skill",
        "summary_ja": "公式プラグインマーケット",
        "description_ja": "Anthropic公式や有志によるプラグイン（スキル/エージェントのバンドル）を配布・取得できるマーケット。",
        "examples": [{"title": "閲覧", "code": "/marketplace"}],
        "links": [], "difficulty": 2, "tier": "free", "related": ["skill-overview"],
    },
    {
        "id": "skill-trigger", "name": "Skill Triggers", "category": "skill",
        "summary_ja": "スキルの自動起動トリガー",
        "description_ja": "SKILL.md の description に書いたキーワードが入力にマッチすると Claude が自動でスキルを呼び出す仕組み。",
        "examples": [{"title": "description例", "code": "description: PRレビューしたい時に使う"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["skill-overview"],
    },

    # ========== MCP ==========
    {
        "id": "mcp-overview", "name": "MCP Overview", "category": "mcp",
        "summary_ja": "Model Context Protocol",
        "description_ja": "外部ツール・APIをClaudeに統合するためのオープンプロトコル。GitHub、Slack、DBなどへの橋渡し。",
        "examples": [{"title": "設定ファイル", "code": ".mcp.json"}],
        "links": [], "difficulty": 3, "tier": "free", "related": ["file-mcp-json", "mcp-stdio", "mcp-sse", "mcp-http"],
    },
    {
        "id": "mcp-stdio", "name": "MCP stdio Server", "category": "mcp",
        "summary_ja": "標準入出力ベースのMCPサーバー",
        "description_ja": "プロセス起動して stdin/stdout でやりとりするMCPサーバー。最も一般的。Pythonやnpx で簡単に動かせる。",
        "examples": [{"title": "設定例", "code": "type: stdio, command: npx, args: [...]"}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["mcp-overview"],
    },
    {
        "id": "mcp-sse", "name": "MCP SSE Server", "category": "mcp",
        "summary_ja": "Server-Sent Events型のMCPサーバー",
        "description_ja": "HTTP経由でストリーミング通信するMCPサーバー。クラウドホスト型サービスに向く。",
        "examples": [{"title": "設定例", "code": "type: sse, url: https://..."}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["mcp-overview"],
    },
    {
        "id": "mcp-http", "name": "MCP HTTP Server", "category": "mcp",
        "summary_ja": "REST/HTTP型のMCPサーバー",
        "description_ja": "標準的なHTTPでやり取りするMCPサーバー。シンプルなリクエスト/レスポンスモデル。",
        "examples": [{"title": "設定例", "code": "type: http, url: https://..."}],
        "links": [], "difficulty": 4, "tier": "free", "related": ["mcp-overview"],
    },

    # ========== Misc / Power Features ==========
    {
        "id": "misc-statusline", "name": "Status Line", "category": "setting",
        "summary_ja": "プロンプト下部のカスタム表示",
        "description_ja": "git ブランチ、モデル名、コンテキスト残量など、自分の好みに合わせて統合バーを表示できる。",
        "examples": [{"title": "skill経由設定", "code": "/statusline-setup"}],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "misc-keybindings", "name": "Keybindings", "category": "setting",
        "summary_ja": "キーボードショートカット",
        "description_ja": "~/.claude/keybindings.json でキー割当をカスタマイズ。chord（複数キー）対応。",
        "examples": [{"title": "ファイル", "code": "~/.claude/keybindings.json"}],
        "links": [], "difficulty": 3, "tier": "free", "related": [],
    },
    {
        "id": "misc-ide-vscode", "name": "VS Code Extension", "category": "setting",
        "summary_ja": "VS Code拡張機能",
        "description_ja": "VS CodeにClaude Codeを統合。エディタ内でClaudeと対話、現在のファイル/選択範囲を即文脈化。",
        "examples": [{"title": "インストール", "code": "VS Code Marketplace で検索"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "misc-ide-jetbrains", "name": "JetBrains Plugin", "category": "setting",
        "summary_ja": "JetBrains IDE プラグイン",
        "description_ja": "IntelliJ / WebStorm / PyCharm などへClaude Codeを統合。VS Code版と同等。",
        "examples": [{"title": "インストール", "code": "JetBrains Marketplace"}],
        "links": [], "difficulty": 1, "tier": "free", "related": [],
    },
    {
        "id": "misc-fast-mode", "name": "Fast Mode", "category": "setting",
        "summary_ja": "高速応答モード",
        "description_ja": "/fast コマンドで Opus 4.6 ベースの高速応答に切替。Opus 4.6 でのみ利用可能。",
        "examples": [{"title": "切替", "code": "/fast"}],
        "links": [], "difficulty": 1, "tier": "free", "related": ["slash-model"],
    },
]


def escape(s: str) -> str:
    return s.replace("'", "''")


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    sql_path = out_dir / "migrations" / "003_seed_standard_features.sql"
    json_path = out_dir / "data" / "features.json"

    sql_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # 公式ドキュメントURLを links 先頭に注入
    for f in FEATURES:
        official_url = get_doc_url(f["id"], f["category"])
        official_link = {"label": "📘 公式ドキュメント", "url": official_url}
        existing_links = f.get("links", [])
        # 既に同URLが入っていれば追加しない
        if not any(l.get("url") == official_url for l in existing_links):
            f["links"] = [official_link] + existing_links

    # JSON 出力
    json_path.write_text(json.dumps({
        "version": "1.1.0-standard-with-docs",
        "updated": "2026-05-02",
        "docs_base": DOCS_BASE,
        "features": FEATURES,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # SQL 出力
    lines = [
        "-- Generated by generate-standard-seed.py",
        "-- Claude Code 標準機能 60+項目のキュレーション",
        "",
        "DELETE FROM features;",
        "",
    ]
    for f in FEATURES:
        examples_json = escape(json.dumps(f.get("examples", []), ensure_ascii=False))
        links_json = escape(json.dumps(f.get("links", []), ensure_ascii=False))
        related_json = escape(json.dumps(f.get("related", []), ensure_ascii=False))
        search = escape(" ".join([f["name"], f["summary_ja"], f["description_ja"]]).lower())

        lines.append(f"""INSERT INTO features (id, name, category, summary_ja, description_ja, examples, links, difficulty, tier, related, search_text)
VALUES (
  '{escape(f['id'])}',
  '{escape(f['name'])}',
  '{f['category']}',
  '{escape(f['summary_ja'])}',
  '{escape(f['description_ja'])}',
  '{examples_json}',
  '{links_json}',
  {f.get('difficulty', 1)},
  '{f.get('tier', 'free')}',
  '{related_json}',
  '{search}'
);""")

    sql_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ {len(FEATURES)} 標準機能を生成")
    by_cat = {}
    for f in FEATURES:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
    for c, n in sorted(by_cat.items()):
        print(f"   {c}: {n}")
    print(f"\nJSON: {json_path}")
    print(f"SQL:  {sql_path}")


if __name__ == "__main__":
    main()
