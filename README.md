# Kameleoon MCP sandbox

Synthetic visitors for QA / internal testing of the Kameleoon MCP and Automation API.

- `site/` - 2-page static site with the Kameleoon snippet (site code `a4hk2ju9x6`), deployed on Netlify as `kameleoon-mcp-sandbox`.
- `bots/web_bot.py` - Playwright bot: each visitor is a fresh browser context, reads its variation, converts with a per-variation probability (known ground truth).
- `bots/sdk_bot.py` - Python SDK bot for feature flags (no browser). Needs `KAMELEOON_CLIENT_ID` / `KAMELEOON_CLIENT_SECRET` in the environment.
- `.github/workflows/web-traffic.yml` - scheduled traffic (about every 20 min, random batch size and start delay).

Notes: Kameleoon rejects the default headless user agent (403 on tracking calls), so the bot sets a normal one. Netlify serves `/pricing.html` as `/pricing`; URL goals must match `/pricing`.

## Running it
Trigger traffic manually: Actions tab -> web-traffic -> Run workflow (set a visitor count). In the working copy of this project the same workflow also runs on a schedule (about every 20 minutes); the schedule is removed here so this copy does not double the traffic.
