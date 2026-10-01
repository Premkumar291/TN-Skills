#!/usr/bin/env python3
"""Screenshot helper for Salesforce docs.

Reads the frontdoor login URL from the SF_FRONTDOOR environment variable so the
session token is never written to disk.

Usage:
    SF_FRONTDOOR="$(sf org open --url-only ...)" python3 tools/shot.py <out.png> <path> [--full] [--wait MS]
"""
import os
import sys
import pathlib

from playwright.sync_api import sync_playwright

VIEWPORT = {"width": 1600, "height": 1000}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}

    if len(args) < 2:
        print(__doc__)
        return 2

    out_path = pathlib.Path(args[0])
    path = args[1]
    full_page = "--full" in flags
    wait_ms = 4000
    for f in flags:
        if f.startswith("--wait="):
            wait_ms = int(f.split("=", 1)[1])

    frontdoor = os.environ.get("SF_FRONTDOOR")
    if not frontdoor:
        print("SF_FRONTDOOR not set", file=sys.stderr)
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        launch_kwargs = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        chrome_path = os.environ.get("CHROME_PATH")
        if chrome_path:
            launch_kwargs["executable_path"] = chrome_path
        browser = p.chromium.launch(**launch_kwargs)
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = ctx.new_page()

        # Establish the session via the frontdoor, then navigate to the target.
        page.goto(frontdoor, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(3000)

        # Setup pages must be served from the my.salesforce.com origin; the
        # post-login redirect lands on lightning.force.com, which sends
        # /lightning/setup/* back to Home. The session cookie is valid for both.
        base = frontdoor.split("/secur/")[0].rstrip("/")

        target = base + path if path.startswith("/") else path
        page.goto(target, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(wait_ms)

        # Never echo the session token back out.
        import re

        safe_url = re.sub(r"(sid=)[^&]*", r"\1<REDACTED>", page.url)
        print("final url:", safe_url)
        print("title    :", page.title())
        if path.strip("/") not in page.url and "login" in page.url.lower():
            print("WARNING: appears to have landed on a login page", file=sys.stderr)
        page.screenshot(path=str(out_path), full_page=full_page)
        print("saved    :", out_path)

        ctx.close()
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
