"""macOS window resolution via Quartz."""
import sys


def get_windows() -> list[dict]:
    """Return list of dicts with keys: title, app, x, y, width, height."""
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
        })
    return windows


def find_window(title: str) -> dict:
    """Return the first window whose app name or title contains `title` (case-insensitive)."""
    needle = title.lower()
    windows = get_windows()
    for w in windows:
        if needle in w["app"].lower() or needle in w["title"].lower():
            return w

    apps = sorted(set(w["app"] for w in windows if w["app"]))
    sys.exit(
        f"No window found matching '{title}'.\n"
        f"Available apps:\n  " + "\n  ".join(apps[:20])
    )
