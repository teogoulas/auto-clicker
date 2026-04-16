import argparse
import time
import sys
import pyautogui

pyautogui.FAILSAFE = True


def resolve_window_offset(title: str, index: int) -> tuple[int, int]:
    from window_utils import find_window
    win = find_window(title, index)
    print(f"Window: '{win['app']} — {win['title']}' at ({win['x']}, {win['y']}), size {win['width']}x{win['height']}")
    return win["x"], win["y"]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Auto-clicker: repeatedly click a screen coordinate at a set interval."
    )
    parser.add_argument("x", type=int, help="X coordinate to click (absolute, or relative to --window)")
    parser.add_argument("y", type=int, help="Y coordinate to click (absolute, or relative to --window)")
    parser.add_argument(
        "--interval", "-i", type=float, default=1.0,
        help="Seconds between clicks (default: 1.0)",
    )
    parser.add_argument(
        "--count", "-n", type=int, default=0,
        help="Number of clicks (0 = unlimited, default: 0)",
    )
    parser.add_argument(
        "--button", "-b", choices=["left", "right", "middle"], default="left",
        help="Mouse button to use (default: left)",
    )
    parser.add_argument(
        "--double", "-d", action="store_true",
        help="Double-click instead of single click",
    )
    parser.add_argument(
        "--window", "-w", type=str, default=None,
        help="Target window title substring. x/y become relative to that window's top-left corner.",
    )
    parser.add_argument(
        "--window-index", type=int, default=0,
        help="Which match to use when multiple windows share the same title (default: 0).",
    )
    return parser.parse_args()


def click(x: int, y: int, button: str, double: bool) -> None:
    if double:
        pyautogui.doubleClick(x, y, button=button)
    else:
        pyautogui.click(x, y, button=button)


def run(x: int, y: int, interval: float, count: int, button: str, double: bool, window: str | None, window_index: int) -> None:
    if window:
        wx, wy = resolve_window_offset(window, window_index)
        x, y = wx + x, wy + y

    click_fn = "Double-click" if double else "Click"
    target = f"({x}, {y})"
    limit = f"{count} times" if count > 0 else "until stopped (Ctrl+C or move mouse to corner)"
    print(f"{click_fn} at {target} every {interval}s — {limit}")

    clicks_done = 0
    try:
        while count == 0 or clicks_done < count:
            click(x, y, button, double)
            clicks_done += 1
            print(f"  [{clicks_done}] clicked at {target}", flush=True)
            if count == 0 or clicks_done < count:
                time.sleep(interval)
    except pyautogui.FailSafeException:
        print("\nFail-safe triggered (mouse moved to corner). Stopping.")
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\nStopped after {clicks_done} click(s).")
        sys.exit(0)

    print(f"Done — {clicks_done} click(s) performed.")


def main():
    args = parse_args()
    run(
        x=args.x,
        y=args.y,
        interval=args.interval,
        count=args.count,
        button=args.button,
        double=args.double,
        window=args.window,
        window_index=args.window_index,
    )


if __name__ == "__main__":
    main()
