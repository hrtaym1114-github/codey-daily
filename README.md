# Codey Daily

Claude Code を毎日5秒で発見するWebアプリ。

> 詳細仕様 / 開発ログは Obsidian Vault で管理:
> `obsidian-1/05_Output/Projects/@Active/Codey-Daily/`

## Stack
- Astro 5 + Tailwind v4 + Cloudflare Pages/Workers
- Hono / Cloudflare D1 / KV
- Stripe Checkout / Web Push (planned)

## Setup
```bash
npm install
wrangler login
# D1 / KV は既に作成済みの場合 wrangler.toml の id を確認
npm run db:migrate
npm run dev
```

## License
MIT
