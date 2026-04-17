"""Window resolution — macOS via Quartz, Windows/Linux via pygetwindow."""
import sys
import platform

_SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"


def get_windows() -> list[dict]:
    """Return list of dicts with keys: app, title, x, y, width, height, layer."""
    if _SYSTEM == "Darwin":
        return _get_windows_mac()
    return _get_windows_other()


def _get_windows_mac() -> list[dict]:
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
        kCGNullWindowID,
    )
    raw = CGWindowListCopyWindowInfo(
        kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements,
        kCGNullWindowID,
    )
    windows = []
    for w in raw:
        bounds = w.get("kCGWindowBounds", {})
        width = int(bounds.get("Width", 0))
        height = int(bounds.get("Height", 0))
        if width < 10 or height < 10:
            continue
        windows.append({
            "app": w.get("kCGWindowOwnerName", ""),
            "title": w.get("kCGWindowName", ""),
            "x": int(bounds.get("X", 0)),
            "y": int(bounds.get("Y", 0)),
            "width": width,
            "height": height,
            "layer": w.get("kCGWindowLayer", 0),
        })
    return windows


def _get_windows_other() -> list[dict]:
    try:
        import pygetwindow as gw
    except ImportError:
        sys.exit("pygetwindow is required on Windows/Linux. Run: pip install pygetwindow")

    windows = []
    for w in gw.getAllWindows():
        if not w.title.strip() or w.width < 10 or w.height < 10:
            continue
        windows.append({
            "app": w.title,   # pygetwindow doesn't separate app name from title
            "title": w.title,
            "x": w.left,
            "y": w.top,
            "width": w.width,
            "height": w.height,
            "layer": 0,       # no layer concept; all treated as normal windows
        })
    return windows


def close_hotkey() -> tuple[str, str]:
    """Return the (modifier, key) pair to close a window on the current platform."""
    return ("command", "w") if _SYSTEM == "Darwin" else ("ctrl", "w")


def _match_score(w: dict, needle: str) -> int:
    app = w["app"].lower()
    title = w["title"].lower()
    if app == needle:
        return 3
    if app.startswith(needle):
        return 2
    if needle in app or needle in title:
        return 1
    return 0


def find_window(title: str, index: int = 0) -> dict:
    """Return the window at `index` among those matching `title`, best matches first."""
    needle = title.lower()
    windows = get_windows()
    matches = sorted(
        [w for w in windows if _match_score(w, needle) > 0],
        key=lambda w: _match_score(w, needle),
        reverse=True,
    )

    if not matches:
        apps = sorted(set(w["app"] for w in windows if w["app"]))
        sys.exit(
            f"No window found matching '{title}'.\n"
            f"Available apps:\n  " + "\n  ".join(apps[:20])
        )

    if len(matches) > 1:
        print(f"Multiple windows match '{title}':")
        for i, w in enumerate(matches):
            marker = " ◀ selected" if i == index else ""
            print(f"  [{i}] {w['app']} — {w['title'] or '(no title)'} at ({w['x']}, {w['y']}){marker}")

    if index >= len(matches):
        sys.exit(f"--window-index {index} is out of range (found {len(matches)} match(es)).")

    return matches[index]
