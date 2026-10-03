#!/usr/bin/env python3
"""Record the project demo walkthrough.

Launches an ISOLATED headed Chromium window (its own profile, so nothing else
on the desktop bleeds in), logs in through the frontdoor SSO link, then walks
the demo sequence with human-paced mouse movement and reading pauses.

Output: demo-recording/demo.webm (converted to .mp4 separately).
"""
import os
import pathlib
import random
import subprocess
import sys

from playwright.sync_api import sync_playwright

CHROME = "/home/killermachine/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
OUT_DIR = pathlib.Path("/home/killermachine/Desktop/study/nm/demo-recording")
PROFILE = pathlib.Path("/tmp/demo-profile")

VIEWPORT = {"width": 1920, "height": 1080}


def frontdoor() -> str:
    """Get a fresh frontdoor SSO URL (kept in-memory only)."""
    r = subprocess.run(
        ["sf", "org", "open", "--target-org", "tp1",
         "--path", "/lightning/setup/Flows/home", "--url-only"],
        capture_output=True, text=True, timeout=120,
    )
    import re
    m = re.search(r"https://\S+", r.stdout.replace("\x1b", ""))
    if not m:
        raise SystemExit("could not obtain frontdoor URL")
    return m.group(0).strip()


def human_move(page, x, y):
    """Move the mouse along a slightly curved path with variable speed."""
    cur = page.evaluate("() => ({x: window.__mx||0, y: window.__my||0})")
    x0, y0 = cur["x"], cur["y"]
    steps = max(12, int(((x - x0) ** 2 + (y - y0) ** 2) ** 0.5 / 12))
    for i in range(1, steps + 1):
        t = i / steps
        # ease-in-out for a natural acceleration profile
        e = 3 * t * t - 2 * t * t * t
        # small perpendicular wobble so the path is not perfectly straight
        wob = 6 * (1 - abs(2 * t - 1)) * (1 if (i % 2) else -1)
        mx = x0 + (x - x0) * e + wob * 0.4
        my = y0 + (y - y0) * e - wob * 0.25
        page.mouse.move(mx, my)
        page.wait_for_timeout(random.randint(8, 22))
    page.evaluate(f"() => {{ window.__mx = {x}; window.__my = {y}; }}")
    page.wait_for_timeout(random.randint(120, 320))


def human_click(page, selector=None, locator=None, settle=900):
    """Realistic click: find it, move there, small pause, click."""
    loc = locator
    if loc is None:
        loc = page.locator(selector).first
    try:
        loc.scroll_into_view_if_needed(timeout=15000)
    except Exception:
        pass
    box = loc.bounding_box(timeout=15000)
    if not box:
        raise RuntimeError(f"no bounding box for {selector or locator}")
    x = box["x"] + box["width"] * (0.35 + 0.3 * random.random())
    y = box["y"] + box["height"] * (0.35 + 0.3 * random.random())
    human_move(page, x, y)
    page.mouse.down()
    page.wait_for_timeout(random.randint(60, 130))
    page.mouse.up()
    page.wait_for_timeout(settle + random.randint(-150, 350))


def type_slow(page, locator, text):
    """Click the field, then type at a human cadence."""
    human_click(page, locator=locator, settle=400)
    for ch in text:
        page.keyboard.type(ch)
        page.wait_for_timeout(random.randint(35, 95))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if PROFILE.exists():
        subprocess.run(["rm", "-rf", str(PROFILE)], check=False)

    fd = frontdoor()
    base = fd.split("/secur/")[0]

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            executable_path=CHROME,
            headless=False,
            viewport=VIEWPORT,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--window-position=0,0", "--window-size=1940,1120",
                  "--start-maximized"],
            record_video_dir=str(OUT_DIR),
            record_video_size=VIEWPORT,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_default_timeout(60000)

        def say(msg):
            print(f"  [{msg}]", flush=True)

        # ---- login ---------------------------------------------------------
        say("login")
        page.goto(fd, wait_until="domcontentloaded")
        page.wait_for_timeout(6000)
        page.evaluate("() => { window.__mx = 800; window.__my = 400; }")

        # ---- 1. Object Manager: the data model -----------------------------
        say("object manager")
        page.goto(base + "/lightning/setup/ObjectManager/home",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(7000)
        page.screenshot(path=str(OUT_DIR / "frame_objectmanager.png"))

        say("object detail")
        page.goto(base + "/lightning/setup/ObjectManager/"
                         "Support_Ticket_Intelligence__c/Details/view",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(7000)

        # ---- 2. Fields & Relationships -------------------------------------
        say("fields")
        page.goto(base + "/lightning/setup/ObjectManager/"
                         "Support_Ticket_Intelligence__c/"
                         "FieldsAndRelationships/view",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        # scroll the field list slowly so the viewer can read it
        for _ in range(4):
            page.mouse.wheel(0, 260)
            page.wait_for_timeout(1100)
        page.wait_for_timeout(1200)

        # ---- 3. Sample data -------------------------------------------------
        say("ticket list")
        page.goto(base + "/lightning/o/Support_Ticket_Intelligence__c/list"
                         "?filterName=00BdM00001PVbXTUA1",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(9000)

        say("ticket record")
        page.goto(base + "/lightning/r/Support_Ticket_Intelligence__c/"
                         "a0AdM00000EUmvBUAT/view",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(9000)

        # ---- 4. Flow --------------------------------------------------------
        say("flow builder")
        page.goto(base + "/builder_platform_interaction/flowBuilder.app"
                         "?flowId=301dM00004E0NVaQAN",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(22000)
        page.mouse.wheel(0, 220)
        page.wait_for_timeout(2500)
        page.mouse.wheel(0, -180)
        page.wait_for_timeout(2500)

        # ---- 5. Permission set ---------------------------------------------
        say("permission set")
        page.goto(base + "/lightning/setup/PermSets/0PSdM00000eK6evWAC/view",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        page.screenshot(path=str(OUT_DIR / "frame_permset.png"))

        # ---- 6. Agentforce Agents ------------------------------------------
        say("agentforce agents")
        page.goto(base + "/lightning/setup/EinsteinCopilot/home",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(10000)

        # ---- 7. Agent Builder + conversation --------------------------------
        say("agent builder")
        page.goto(base + "/AiCopilot/copilotStudio.app#/copilot/builder"
                         "?copilotId=0XxdM000004WDzASAW"
                         "&versionId=0X9dM000008TxjKSAS",
                  wait_until="domcontentloaded")
        page.wait_for_timeout(24000)

        # make sure the Conversation Preview pane has real width before typing
        say("open preview")
        try:
            page.evaluate("""() => {
              const btns = Array.from(document.querySelectorAll('button'))
                .filter(b => /expand|preview/i.test((b.getAttribute('title')||'') + ' ' + (b.textContent||'')));
              if (btns.length) btns[0].click();
            }""")
            page.wait_for_timeout(2500)
        except Exception:
            pass

        # widen the composer if it is collapsed
        w = page.evaluate("""() => {
          const t = Array.from(document.querySelectorAll('textarea'))
            .find(e => /Describe your task/i.test(e.placeholder || ''));
          return t ? Math.round(t.getBoundingClientRect().width) : -1;
        }""")
        print(f"   composer width: {w}px", flush=True)
        if w != -1 and w < 120:
            page.evaluate("""() => {
              const t = Array.from(document.querySelectorAll('textarea'))
                .find(e => /Describe your task/i.test(e.placeholder || ''));
              if (t) { t.style.minWidth = '520px'; t.style.width = '520px'; }
            }""")
            page.wait_for_timeout(1200)

        say("conversation")
        questions = [
            "What is the priority of the support ticket for Acme Corporation?",
            "What is the priority of the support ticket for Globex Systems?",
            "What is the priority of the support ticket for Initech Solutions?",
        ]
        for q in questions:
            ok = False
            try:
                ta = page.locator("textarea[placeholder*='Describe your task']").first
                ta.wait_for(state="visible", timeout=20000)
                type_slow(page, ta, q)
                page.wait_for_timeout(900)
                # send: prefer the Send button, fall back to Enter
                sent = page.evaluate("""() => {
                  const b = Array.from(document.querySelectorAll('button'))
                    .find(x => ((x.getAttribute('title')||x.getAttribute('aria-label')||'')
                                 .toLowerCase() === 'send'));
                  if (b) { b.click(); return 'button'; }
                  return 'none';
                }""")
                if sent == 'none':
                    page.keyboard.press("Enter")
                ok = True
                page.wait_for_timeout(17000)
            except Exception as e:
                print("   chat step failed:", str(e)[:100], flush=True)
            print(f"   asked: {q[:52]}... ({'sent' if ok else 'FAILED'})", flush=True)

        page.wait_for_timeout(4000)

        vpath = page.video.path() if page.video else None
        ctx.close()

    # playwright names the file; normalise it
    webms = sorted(OUT_DIR.glob("*.webm"), key=lambda f: f.stat().st_mtime)
    if webms:
        target = OUT_DIR / "demo.webm"
        if webms[-1] != target:
            webms[-1].rename(target)
        print("  video:", target, f"{target.stat().st_size/1024/1024:.1f} MB")
    else:
        print("  no video produced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
