"""
Interactive pixel locator.

Run this script, move your mouse to the target pixel, and press Enter to record it.
Press Ctrl+C to exit. Coordinates are printed in a format ready to paste into main.py.
"""
import sys
import time
import pyautogui

pyautogui.FAILSAFE = False


def live_mode():
    """Continuously print mouse position until Ctrl+C."""
    print("Live mode — move your mouse. Press Ctrl+C to stop.\n")
    prev = None
    try:
        while True:
            pos = pyautogui.position()
            if pos != prev:
                r, g, b, *_ = pyautogui.screenshot().getpixel(pos)
                print(f"\r  x={pos.x:<6} y={pos.y:<6} rgb=({r},{g},{b})    ", end="", flush=True)
                prev = pos
            time.sleep(0.05)
    except KeyboardInterrupt:
        print(f"\n\nFinal position: x={prev.x} y={prev.y}")


def capture_mode():
    """Press Enter to snapshot the current mouse position; Ctrl+C to finish."""
    print("Capture mode — position your mouse and press Enter to record. Ctrl+C to finish.\n")
    captured = []
    try:
        while True:
            input("  Press Enter to capture current position...")
            pos = pyautogui.position()
            r, g, b, *_ = pyautogui.screenshot().getpixel(pos)
            entry = f"x={pos.x} y={pos.y} rgb=({r},{g},{b})"
            captured.append((pos.x, pos.y))
            print(f"  Captured: {entry}\n")
    except KeyboardInterrupt:
        pass

    if captured:
        print("\nCaptured coordinates (ready to use with main.py):")
        for x, y in captured:
            print(f"  python main.py {x} {y}")


def list_windows():
    """Print all visible window titles and their positions."""
    try:
        import pygetwindow as gw
    except ImportError:
        sys.exit("pygetwindow not installed. Run: pip install pygetwindow")

    windows = [w for w in gw.getAllWindows() if w.title.strip()]
    if not windows:
        print("No windows found.")
        return

    print(f"{'Title':<50} {'Left':>6} {'Top':>6} {'Width':>7} {'Height':>7}")
    print("-" * 80)
    for w in windows:
        print(f"{w.title[:49]:<50} {w.left:>6} {w.top:>6} {w.width:>7} {w.height:>7}")


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
