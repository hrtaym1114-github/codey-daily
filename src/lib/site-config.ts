/**
 * Codey Daily — サイト設定（公開可能な情報のみ）
 *
 * 注意: 全ての値はビルド時にHTMLにインライン化されます。
 * 秘密情報（API key等）は Cloudflare Workers Secrets を使ってください。
 */

// ========== Cloudflare Web Analytics ==========
// 取得方法:
//   1. https://dash.cloudflare.com にログイン
//   2. 左メニュー「Analytics & Logs」→「Web Analytics」
//   3. 「Add a site」→「Manual setup」を選択
//   4. Hostname: codey-daily.hrtaym1114.workers.dev
//   5. 表示される snippet の data-cf-beacon='{"token": "XXX"}' の XXX を下にペースト
export const CF_BEACON_TOKEN = '';  // ← ここに token を貼る

// ========== サイト基本情報 ==========
export const SITE_URL = 'https://codey-daily.hrtaym1114.workers.dev';
export const SITE_NAME = 'Codey Daily';
export const SITE_DESCRIPTION = 'Claude Code を毎日5秒で発見するWebアプリ';

// ========== GitHub / Sponsor ==========
export const GITHUB_USER = 'hrtaym1114-github';
export const GITHUB_REPO = 'codey-daily';
export const GITHUB_REPO_URL = `https://github.com/${GITHUB_USER}/${GITHUB_REPO}`;
export const SPONSOR_URL = `https://github.com/sponsors/${GITHUB_USER}`;

// ========== Social ==========
export const X_HANDLE = 'Amu_Lab__';
export const X_PROFILE_URL = `https://x.com/${X_HANDLE}`;
