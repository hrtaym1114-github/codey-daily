---
title: "I built a daily Claude Code feature discovery app"
published: false
description: "Catch up with every Claude Code release in 5 seconds a day. Auto-synced via GitHub Actions + Claude Code Action."
tags: claudecode, ai, indiehackers, buildinpublic
canonical_url: https://codey.bhrtaym-blog.com/
cover_image:
---

## TL;DR

- **Codey Daily** discovers Claude Code's 94 standard features for you, one per day
- Auto-synced to the official CHANGELOG via GitHub Actions + Claude Code Action
- Runs entirely on **Cloudflare's free tier** — practically $0/month
- Live: https://codey.bhrtaym-blog.com
- Source: https://github.com/hrtaym1114-github/codey-daily

## Why I built it

Claude Code ships fast. New slash commands, hooks, skills, MCP servers — every week.

The official CHANGELOG is a wall of text. Discord and personal blogs eat too much of my time. I kept catching myself **using Claude Code without knowing about features I would have wanted**.

So I built a tiny daily habit: **one feature, 5 seconds, every morning**.

## What it does

| Feature | Description |
|---|---|
| 📅 Today's card | A single feature with summary + code example |
| 🃏 Flashcards | Flip-style spaced learning |
| 🎯 Quiz | 4-option multiple choice |
| 📜 Changelog | Searchable, categorized release notes |
| 🔥 Streak | Day-streak tracker after Google login |
| 🤖 Auto-sync | Pulls Claude Code's CHANGELOG daily |

## Architecture

```
Claude Code CHANGELOG
        │ (daily 03:00 JST)
        ▼
GitHub Actions + Claude Code Action  ← detects new features
        │
        ▼
data/features.json (auto-PR)
        │
        ▼
Astro static build
        │
        ▼
Cloudflare Workers + D1 + KV
```

## Stack

- **Frontend**: Astro 6 + Tailwind v4
- **Hosting**: Cloudflare Workers (static + edge SSR)
- **DB**: D1 (SQLite) for streak tracking
- **Auth**: Google OAuth (optional)
- **Auto-sync**: GitHub Actions + [Claude Code Action](https://github.com/anthropics/claude-code-action)
- **Analytics**: Cloudflare Web Analytics

## Lessons learned

### 1. Claude Code Action is shockingly good for "just figure it out" diffs

I started with regex parsing of the CHANGELOG. Brittle. Replaced the whole step with:

```yaml
- name: Auto-add new features
  uses: anthropic/claude-code-action@v1
  with:
    prompt: |
      Add new feature entries to data/features.json based on
      the latest CHANGELOG diff. Use existing entries as a template.
```

Just works. PRs land with proper category, summary, and example code.

### 2. Cloudflare Web Analytics counts "Visits" weirdly

Direct/bookmark traffic shows as 0 visits because there's no referrer. Use GA4 alongside if you want accurate numbers.

### 3. Astro 6 + `@astrojs/cloudflare` works best with `output: 'static'`

Mixing SSR triggers D1/KV evaluation at build time and creates pain. Static-first, edge for the rare dynamic route.

## What's next

- English content pipeline (auto-translate via LLM)
- Daily email digest
- Claude Code plugin distribution (`/codey-today` slash command)
- Leaderboards

## Support the project

- ⭐ Star: https://github.com/hrtaym1114-github/codey-daily
- ❤️ Sponsor: https://github.com/sponsors/hrtaym1114-github
- 🐦 X: [@Amu_Lab__](https://x.com/Amu_Lab__)

Feedback / feature requests welcome in the comments!
