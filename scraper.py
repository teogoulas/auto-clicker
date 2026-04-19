import argparse
import platform
import subprocess
import time

from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aegean College e-learning automator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--username", required=True, help="Login username or e-mail")
    parser.add_argument("--password", required=True, help="Login password")
    parser.add_argument("--section", required=True, help="Section name to expand (case-insensitive substring match)")
    parser.add_argument("--subsection", required=True, help="Sub-section to click (case-insensitive substring match)")
    parser.add_argument("--next-interval", type=float, default=30.0, metavar="SECONDS",
                        help="Seconds between 'Next >' clicks in the slideshow")
    parser.add_argument("--cycle-interval", type=float, default=60.0, metavar="MINUTES",
                        help="Minutes per cycle before logging out and restarting")
    parser.add_argument("--cycles", type=int, default=4, help="Number of login/logout cycles to run")
    return parser.parse_args()


def login(page: Page, username: str, password: str) -> None:
    print("[login] Navigating to login page...")
    page.goto("https://ops.aegeancollege.gr/login?returnUrl=%2f")
    page.wait_for_load_state("networkidle")

    # Username field — try placeholder text first, fall back to input type
    username_field = page.get_by_placeholder("Όνομα χρήστη ή e-Mail")
    if not username_field.is_visible():
        username_field = page.locator("input[name='username'], input[type='text']").first
    username_field.fill(username)

    # Password field
    page.locator("input[type='password']").first.fill(password)

    # Submit — "Σύνδεση" button
    page.get_by_text("Σύνδεση", exact=True).click()
    page.wait_for_load_state("networkidle")
    print("[login] Logged in.")


def navigate_to_course(page: Page) -> None:
    print("[nav] Clicking 'Κατάρτιση'...")
    page.get_by_text("Κατάρτιση", exact=True).first.click()
    page.wait_for_load_state("networkidle")

    print("[nav] Clicking 'Άνοιγμα μαθημάτων'...")
    page.get_by_text("Άνοιγμα μαθημάτων").first.click()
    page.wait_for_load_state("networkidle")

    print("[nav] Switching to 'Τα μαθήματά μου'...")
    page.get_by_text("Τα μαθήματά μου").first.click()
    page.wait_for_load_state("networkidle")

    print("[nav] Clicking course card...")
    page.locator("a").filter(has_text="Εφαρμογές Τεχνητής Νοημοσύνης").first.click()
    page.wait_for_load_state("networkidle")
    print("[nav] On course page.")


def expand_section(page: Page, section_text: str) -> None:
    print(f"[section] Looking for section: '{section_text}'...")
    needle = section_text.lower()

    # Moodle-style section headings — try multiple selector patterns
    candidates = page.locator(
        "h3, h4, h5, "
        "[class*='section-title'], [class*='sectionname'], "
        "[class*='topic'], [data-sectionid], "
        ".section .content .sectionname, "
        "[aria-expanded]"
    ).all()

    for el in candidates:
        try:
            text = el.inner_text(timeout=1000).strip()
        except Exception:
            continue
        if needle in text.lower():
            print(f"[section] Found: '{text}' — clicking to expand...")
            el.click()
            page.wait_for_timeout(800)
            return

    raise ValueError(
        f"Section '{section_text}' not found on {page.url}\n"
        f"Available headings: {[el.inner_text(timeout=500) for el in candidates[:20]]}"
    )


def open_subsection(page: Page, subsection_text: str) -> None:
    print(f"[subsection] Looking for subsection: '{subsection_text}'...")
    needle = subsection_text.lower()

    candidates = page.locator(
        "[class*='activity'] a, [class*='resource'] a, "
        "[class*='modtype'] a, li.activity a, "
        ".activityname, [class*='instancename']"
    ).all()

    for el in candidates:
        try:
            text = el.inner_text(timeout=1000).strip()
        except Exception:
            continue
        if needle in text.lower():
            print(f"[subsection] Found: '{text}' — clicking...")
            el.click()
            page.wait_for_load_state("networkidle")
            return

    raise ValueError(
        f"Subsection '{subsection_text}' not found on {page.url}\n"
        f"Candidates checked: {len(candidates)}"
    )


def enter_lesson(page: Page, context: BrowserContext) -> Page:
    print("[lesson] Clicking 'Είσοδος/Σύνδεση' and waiting for slideshow window...")
    try:
        with context.expect_page(timeout=15_000) as new_page_info:
            page.get_by_text("Είσοδος/Σύνδεση").first.click()
        slide_page = new_page_info.value
    except PlaywrightTimeoutError:
        raise RuntimeError(
            "Slideshow window did not open after clicking 'Είσοδος/Σύνδεση'. "
            "Check that the subsection was opened correctly."
        )
    slide_page.wait_for_load_state("domcontentloaded")
    print(f"[lesson] Slideshow opened: {slide_page.url}")
    return slide_page


def _play_and_mute(slide_page: Page) -> None:
    """Attempt to play and mute video via JS across all frames, then via UI buttons."""
    js = """
        document.querySelectorAll('video, audio').forEach(v => {
            v.muted = true;
            v.volume = 0;
            try { v.play(); } catch(e) {}
        });
    """
    for frame in slide_page.frames:
        try:
            frame.evaluate(js)
        except Exception:
            pass

    # Click play/mute buttons — try broad selectors across all frames
    play_selectors = [
        "button[title*='Play' i]",
        "[class*='play-button']",
        "[aria-label*='play' i]",
        "[class*='playBtn']",
        "[class*='PlayButton']",
        "button:nth-child(1)",  # first button in player controls
    ]
    mute_selectors = [
        "[class*='collapsable-button']",
        "[class*='collapsed-control']",
        "button[title*='Mute' i]",
        "button[title*='Sound' i]",
        "button[title*='Audio' i]",
        "[aria-label*='mute' i]",
        "[aria-label*='sound' i]",
        "[aria-label*='audio' i]",
        "[class*='mute']",
        "[class*='volume']",
        "[class*='sound']",
        "[class*='audio']",
    ]
    for frame in slide_page.frames:
        for sel in play_selectors:
            try:
                frame.locator(sel).first.click(timeout=1500)
                print("[slideshow] Clicked play button.")
                break
            except Exception:
                pass
        for sel in mute_selectors:
            try:
                frame.locator(sel).first.click(timeout=1500)
                print("[slideshow] Clicked mute button.")
                break
            except Exception:
                pass


def _click_next(slide_page: Page) -> bool:
    """Click the Next button; return True if successful."""
    next_selectors = [
        "button:has-text('Next')",
        "button:has-text('Επόμενο')",
        "a:has-text('Next')",
        "[class*='next-btn']",
        "[class*='nextBtn']",
        "[aria-label*='next' i]",
        "[id*='next']",
        "input[value*='Next' i]",
    ]
    for frame in slide_page.frames:
        for sel in next_selectors:
            try:
                frame.locator(sel).first.click(timeout=2000)
                return True
            except Exception:
                pass
    return False


def run_slideshow(slide_page: Page, next_interval: float, deadline: float) -> None:
    print("[slideshow] Starting play/mute setup...")
    page_load_grace = 3.0
    time.sleep(page_load_grace)
    _play_and_mute(slide_page)

    print(f"[slideshow] Clicking 'Next >' every {next_interval}s until cycle ends...")
    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        sleep_for = min(next_interval, remaining)
        if sleep_for <= 0:
            break
        time.sleep(sleep_for)

        if time.monotonic() >= deadline:
            break

        ok = _click_next(slide_page)
        if ok:
            print(f"[slideshow] Clicked Next >  (remaining: {int(deadline - time.monotonic())}s)")
        else:
            print("[slideshow] Next button not found — will retry next interval.")

    print("[slideshow] Cycle deadline reached.")


def logout(page: Page) -> None:
    print("[logout] Navigating to portal home...")
    page.goto("https://ops.aegeancollege.gr/")
    page.wait_for_load_state("networkidle")

    print("[logout] Clicking avatar/profile menu...")
    page.locator("[onclick*='toggleMenuItem']").last.click(timeout=10_000)
    page.wait_for_timeout(500)

    print("[logout] Clicking logout button...")
    page.locator("button.menu-logout").first.click()
    page.wait_for_load_state("networkidle")
    print("[logout] Logged out.")


def main() -> None:
    args = parse_args()

    system = platform.system()
    if system == "Darwin":
        keep_awake = subprocess.Popen(["caffeinate", "-d"])
    elif system == "Linux":
        try:
            keep_awake = subprocess.Popen(["xdg-screensaver", "reset"])
        except FileNotFoundError:
            keep_awake = None
    else:
        keep_awake = None  # Windows: no built-in equivalent needed; set power plan manually
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False, slow_mo=200)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(60_000)

            for cycle_num in range(1, args.cycles + 1):
                print(f"\n=== Cycle {cycle_num}/{args.cycles} ===")
                deadline = time.monotonic() + args.cycle_interval * 60

                login(page, args.username, args.password)
                navigate_to_course(page)
                expand_section(page, args.section)
                open_subsection(page, args.subsection)
                slide_page = enter_lesson(page, context)
                slide_page.set_default_timeout(60_000)

                run_slideshow(slide_page, args.next_interval, deadline)

                slide_page.close()
                logout(page)

            browser.close()
            print("\nAll cycles complete.")
    finally:
        if keep_awake is not None:
            keep_awake.terminate()


if __name__ == "__main__":
    main()
