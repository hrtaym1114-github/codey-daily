#!/usr/bin/env python3
"""
Codey Daily — Claude Code 標準機能の初期データ生成

ayumu 自作のVault素材ではなく、Claude Code 組み込み機能のキュレーションを生成。
"""
import json
import sys
from pathlib import Path

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

    # JSON 出力
    json_path.write_text(json.dumps({
        "version": "1.0.0-standard",
        "updated": "2026-05-01",
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
