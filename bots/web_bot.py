"""Browser bot: simulates visitors on the MCP Sandbox site.

Each visitor = fresh browser context (new Kameleoon visitor code), realistic UA,
random think-time. Conversion probability depends on the variation the visitor was
bucketed into, so experiment results have a KNOWN ground truth to validate against.

Usage:
  python web_bot.py --base https://kameleoon-mcp-sandbox.netlify.app --visitors 20
  python web_bot.py --base http://localhost:8000 --visitors 3 --headed   # local dry run
"""
import argparse
import random
import time

from playwright.sync_api import sync_playwright

UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]

# Ground truth: P(click CTA) per variation name. Anything not listed uses "default".
CTA_RATE = {"default": 0.10, "Original": 0.10, "Variation 1": 0.12}
# P(start trial | reached pricing)
TRIAL_RATE = 0.25


def active_variations(page):
    """Return {experimentId: variationName} the visitor is bucketed into (empty if none)."""
    try:
        page.wait_for_function("window.Kameleoon && Kameleoon.API && Kameleoon.API.Experiments", timeout=4000)
        return page.evaluate(
            "Kameleoon.API.Experiments.getActive().map(e => ({id: e.id, v: e.associatedVariation && e.associatedVariation.name}))"
        )
    except Exception:
        return []


def run_visitor(browser, base, i, headed):
    ctx = browser.new_context(
        user_agent=random.choice(UAS),
        viewport={"width": random.choice([1440, 1280, 390]), "height": 900},
    )
    page = ctx.new_page()
    page.goto(base + "/", wait_until="load")
    page.wait_for_timeout(random.randint(800, 2500))
    acts = active_variations(page)
    rate = CTA_RATE["default"]
    for a in acts:
        name = (a.get("v") or "").lower()
        rate = CTA_RATE["Original"] if ("orig" in name or "refer" in name) else CTA_RATE["Variation 1"]
    clicked = random.random() < rate
    trial = False
    if clicked:
        page.click("#cta-button")
        page.wait_for_load_state("load")
        page.wait_for_timeout(random.randint(500, 2000))
        if random.random() < TRIAL_RATE:
            page.click("#trial-button")
            trial = True
            page.wait_for_timeout(800)
    # give the engine time to flush tracking requests
    page.wait_for_timeout(1500)
    ctx.close()
    print(f"visitor {i}: experiments={acts} cta={clicked} trial={trial}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--visitors", type=int, default=20)
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not a.headed)
        for i in range(a.visitors):
            run_visitor(browser, a.base.rstrip("/"), i, a.headed)
            time.sleep(random.uniform(0.2, 1.0))
        browser.close()


if __name__ == "__main__":
    main()
