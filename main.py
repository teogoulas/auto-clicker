import argparse
import time
import sys
import pyautogui

pyautogui.FAILSAFE = True


# ---------------------------------------------------------------------------
# locate subcommand
# ---------------------------------------------------------------------------

def window_at(x: int, y: int):
    from window_utils import get_windows
    for w in get_windows():
        if w["layer"] != 0:
            continue
        if w["x"] <= x < w["x"] + w["width"] and w["y"] <= y < w["y"] + w["height"]:
            return w
    return None


def format_line(pos, r, g, b):
    win = window_at(pos.x, pos.y)
    abs_part = f"abs=({pos.x},{pos.y})"
    if win:
        rx, ry = pos.x - win["x"], pos.y - win["y"]
        return f"  {abs_part}  rel=({rx},{ry})  window='{win['app']}'  rgb=({r},{g},{b})"
    return f"  {abs_part}  rgb=({r},{g},{b})"


def locate_live():
    print("Live mode — move your mouse. Press Ctrl+C to stop.\n")
    prev = None
    try:
        while True:
            pos = pyautogui.position()
            if pos != prev:
                r, g, b, *_ = pyautogui.screenshot().getpixel(pos)
                print(f"\r{format_line(pos, r, g, b)}    ", end="", flush=True)
                prev = pos
            time.sleep(0.05)
    except KeyboardInterrupt:
        print()


def locate_capture():
    print("Capture mode — position your mouse and press Enter to record. Ctrl+C to finish.\n")
    captured = []
    try:
        while True:
            input("  Press Enter to capture current position...")
            pos = pyautogui.position()
            r, g, b, *_ = pyautogui.screenshot().getpixel(pos)
            print(f"{format_line(pos, r, g, b)}\n")
            captured.append((pos.x, pos.y, window_at(pos.x, pos.y)))
    except KeyboardInterrupt:
        pass

    if captured:
        print("\nReady-to-use commands:")
        for x, y, win in captured:
            if win:
                rx, ry = x - win["x"], y - win["y"]
                print(f'  python main.py click {rx} {ry} --window "{win["app"]}"')
            else:
                print(f"  python main.py click {x} {y}")


def locate_windows():
    from window_utils import get_windows
    windows = get_windows()
    if not windows:
        print("No windows found.")
        return
    print(f"{'App':<30} {'Title':<30} {'X':>6} {'Y':>6} {'Width':>7} {'Height':>7}")
    print("-" * 90)
    for w in windows:
        print(f"{w['app'][:29]:<30} {w['title'][:29]:<30} {w['x']:>6} {w['y']:>6} {w['width']:>7} {w['height']:>7}")


def cmd_locate(args):
    if args.mode == "live":
        locate_live()
    elif args.mode == "windows":
        locate_windows()
    else:
        locate_capture()


# ---------------------------------------------------------------------------
# click subcommand
# ---------------------------------------------------------------------------

def resolve_window_offset(title: str, index: int) -> tuple[int, int]:
    from window_utils import find_window
    win = find_window(title, index)
    print(f"Window: '{win['app']} — {win['title']}' at ({win['x']}, {win['y']}), size {win['width']}x{win['height']}")
    return win["x"], win["y"]


def do_click(x: int, y: int, button: str, double: bool) -> None:
    if double:
        pyautogui.doubleClick(x, y, button=button)
    else:
        pyautogui.click(x, y, button=button)


def cmd_click(args):
    x, y = args.x, args.y

    if args.window:
        wx, wy = resolve_window_offset(args.window, args.window_index)
        x, y = wx + x, wy + y

    click_fn = "Double-click" if args.double else "Click"
    target = f"({x}, {y})"
    limit = f"{args.count} times" if args.count > 0 else "until stopped (Ctrl+C or move mouse to corner)"
    close_msg = f" — window closes after {args.close_after} min" if args.close_after else ""
    print(f"{click_fn} at {target} every {args.interval}s — {limit}{close_msg}")

    deadline = time.monotonic() + args.close_after * 60 if args.close_after else None
    clicks_done = 0
    try:
        while args.count == 0 or clicks_done < args.count:
            if deadline and time.monotonic() >= deadline:
                break
            do_click(x, y, args.button, args.double)
            clicks_done += 1
            print(f"  [{clicks_done}] clicked at {target}", flush=True)
            if args.count == 0 or clicks_done < args.count:
                time.sleep(args.interval)
    except pyautogui.FailSafeException:
        print("\nFail-safe triggered (mouse moved to corner). Stopping.")
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\nStopped after {clicks_done} click(s).")
        sys.exit(0)

    if deadline and time.monotonic() >= deadline:
        print("\nTime's up — closing window.")
        pyautogui.hotkey("command", "w")

    print(f"Done — {clicks_done} click(s) performed.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Auto-clicker with pixel/window discovery.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # locate
    p_locate = sub.add_parser("locate", help="Discover pixel coordinates and windows.")
    p_locate.add_argument(
        "mode", nargs="?", default="capture",
        choices=["capture", "live", "windows"],
        help="capture (default): press Enter to record | live: stream position | windows: list windows",
    )

    # click
    p_click = sub.add_parser("click", help="Repeatedly click a coordinate.")
    p_click.add_argument("x", type=int, help="X coordinate (absolute, or relative to --window)")
    p_click.add_argument("y", type=int, help="Y coordinate (absolute, or relative to --window)")
    p_click.add_argument("--interval", "-i", type=float, default=10.0, help="Seconds between clicks (default: 10)")
    p_click.add_argument("--count", "-n", type=int, default=0, help="Total clicks, 0 = unlimited (default: 0)")
    p_click.add_argument("--button", "-b", choices=["left", "right", "middle"], default="left")
    p_click.add_argument("--double", "-d", action="store_true", help="Double-click")
    p_click.add_argument("--window", "-w", type=str, default=None, help="Target window title substring")
    p_click.add_argument("--window-index", type=int, default=0, help="Which match to use (default: 0)")
    p_click.add_argument("--close-after", "-c", type=float, default=None, metavar="MINUTES",
                         help="Close window with Cmd+W after this many minutes, then exit")

    args = parser.parse_args()
    if args.cmd == "locate":
        cmd_locate(args)
    else:
        cmd_click(args)


if __name__ == "__main__":
    main()
