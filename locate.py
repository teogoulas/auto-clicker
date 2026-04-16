"""
Interactive pixel locator.

Run this script, move your mouse to the target pixel, and press Enter to record it.
Press Ctrl+C to exit. Coordinates are printed in a format ready to paste into main.py.
"""
import sys
import time
import pyautogui

pyautogui.FAILSAFE = False


def window_at(x: int, y: int):
    """Return the topmost window containing (x, y), or None."""
    from window_utils import get_windows
    for w in get_windows():
        if w["x"] <= x < w["x"] + w["width"] and w["y"] <= y < w["y"] + w["height"]:
            return w
    return None


def format_line(pos, r, g, b):
    win = window_at(pos.x, pos.y)
    abs_part = f"abs=({pos.x},{pos.y})"
    if win:
        rx, ry = pos.x - win["x"], pos.y - win["y"]
        name = win["app"]
        return f"  {abs_part}  rel=({rx},{ry})  window='{name}'  rgb=({r},{g},{b})"
    return f"  {abs_part}  rgb=({r},{g},{b})"


def live_mode():
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


def capture_mode():
    print("Capture mode — position your mouse and press Enter to record. Ctrl+C to finish.\n")
    captured = []
    try:
        while True:
            input("  Press Enter to capture current position...")
            pos = pyautogui.position()
            r, g, b, *_ = pyautogui.screenshot().getpixel(pos)
            print(f"{format_line(pos, r, g, b)}\n")
            win = window_at(pos.x, pos.y)
            captured.append((pos.x, pos.y, win))
    except KeyboardInterrupt:
        pass

    if captured:
        print("\nReady-to-use commands:")
        for x, y, win in captured:
            if win:
                rx, ry = x - win["x"], y - win["y"]
                print(f'  python main.py {rx} {ry} --window "{win["app"]}"')
            else:
                print(f"  python main.py {x} {y}")


def list_windows():
    from window_utils import get_windows
    windows = get_windows()
    if not windows:
        print("No windows found.")
        return

    print(f"{'App':<30} {'Title':<30} {'X':>6} {'Y':>6} {'Width':>7} {'Height':>7}")
    print("-" * 90)
    for w in windows:
        print(f"{w['app'][:29]:<30} {w['title'][:29]:<30} {w['x']:>6} {w['y']:>6} {w['width']:>7} {w['height']:>7}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pixel and window discovery tool.")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("live", help="Continuously print mouse position and pixel color.")
    sub.add_parser("capture", help="Press Enter to snapshot mouse position (default).")
    sub.add_parser("windows", help="List all visible windows with their screen positions.")
    args = parser.parse_args()

    if args.cmd == "live":
        live_mode()
    elif args.cmd == "windows":
        list_windows()
    else:
        capture_mode()


if __name__ == "__main__":
    main()
