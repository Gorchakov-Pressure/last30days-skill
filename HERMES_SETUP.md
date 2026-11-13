# Hermes Setup Guide for last30days

This guide covers installing last30days on Hermes AI Agent.

## Prerequisites

1. **Hermes installed** - See https://github.com/NousResearch/hermes-agent
2. **Python 3.12+** - `brew install python@3.12` or similar
3. **yt-dlp** (optional, for YouTube) - `brew install yt-dlp`

## Installation

Use the normal guarded installer with the explicit skill path:

```bash
hermes skills install mvanhorn/last30days-skill/skills/last30days
hermes skills list
```

This GitHub identifier resolves the repository's default branch; Hermes records the resolved tree commit. It does not select an arbitrary branch or SHA. Verify that the recorded commit matches the reviewed release before using the skill. A direct SKILL.md URL is not an equivalent whole-bundle installation: it can omit runtime modules.

Keep native quarantine, full-bundle scanning, and policy checks enabled. If fetching or policy blocks installation, or the recorded commit does not match the reviewed source, stop and report the exact result. Do not force installation, copy or link a checkout into the skills directory, weaken security controls, or omit files to change the verdict. A caution verdict can still block a community installation; this patch does not establish acceptance. Static text regressions are not the native scanner. After a successful installation, confirm the skill appears in the intended profile with `hermes skills list`.

## Usage

In Hermes, invoke with:

```
last30days "your research topic"
```

Or with options:
```
last30days "best mechanical keyboards 2025" --search=reddit,youtube
last30days "AI news" --days=7 --deep
```

## First Run Setup

On first run, the skill will guide you through setup:

1. **Auto setup** (~30 seconds)
   - Scans browser cookies for X/Twitter
   - Checks/installs yt-dlp for YouTube
   - Best-effort install of `digg-pp-cli` for Digg story clusters (via `@mvanhorn/printing-press-library`; binary lands in `$HOME/.local/bin` — ensure your Hermes gateway PATH includes it, or Digg stays off even after install)
   - Configures free sources (Reddit, HN, Polymarket)

2. **Optional: ScrapeCreators**
   - Adds TikTok, Instagram, Reddit backup
   - 100 free credits (no expiration)
   - Sign up at scrapecreators.com

3. **Optional: API Keys**
   - XAI_API_KEY for X/Twitter (alternative to browser cookies)
   - BRAVE_API_KEY for web search

## Available Sources

### Free (No API Key)
- **Reddit** - Public discussions and comments
- **Hacker News** - Tech discussions via Algolia
- **Polymarket** - Prediction markets
- **YouTube** - Search and transcripts (requires yt-dlp)
- **Digg** - story clusters from every Digg topic, ranked by Digg Score (requires `digg-pp-cli` on the agent PATH; auto-installed to `$HOME/.local/bin` during setup when `npx` is available)

### Requires API Key
- **X/Twitter** - xAI API key or browser cookies
- **TikTok** - ScrapeCreators API
- **Instagram** - ScrapeCreators API
- **Web Search** - Brave Search API

## Troubleshooting

### Python not found
```bash
# Find Python 3.12+
which python3.12 python3.13 python3.14

# If not installed
brew install python@3.12
```

### yt-dlp not found
```bash
brew install yt-dlp
# or
pip install yt-dlp
```

### Check what's configured
```bash
cd ~/.hermes/skills/research/last30days
python3.12 scripts/last30days.py --diagnose
```

## Updating

Review the new source revision, then use the same guarded installation path. A previous successful install does not authorize a new revision; stop on any fetch or policy refusal.

## Support

- Original repo: https://github.com/mvanhorn/last30days-skill
- Hermes: https://github.com/mercurial-tf/hermes
- Issues: Please report in the original repo
