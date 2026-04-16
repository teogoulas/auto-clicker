# auto-clicker

Repeatedly click a screen coordinate at a configurable interval. Supports window-relative targeting and interactive pixel discovery.

## Setup

```bash
conda env create -f environment.yml
conda activate auto-clicker
```

> **macOS**: grant Terminal (or your IDE) accessibility permissions in  
> *System Preferences → Privacy & Security → Accessibility*.

---

## Usage

### `main.py` — click a pixel

```
python main.py <x> <y> [options]
```

| Argument | Default | Description |
|---|---|---|
| `x`, `y` | required | Absolute screen coordinates, or relative to `--window` |
| `--interval`, `-i` | `1.0` | Seconds between clicks |
| `--count`, `-n` | `0` | Total clicks (0 = unlimited) |
| `--button`, `-b` | `left` | `left` / `right` / `middle` |
| `--double`, `-d` | off | Double-click |
| `--window`, `-w` | — | Window title substring; makes x/y relative to that window |

**Examples**

```bash
# Click absolute coordinate (960, 540) every 2 seconds
python main.py 960 540 --interval 2

# Click 50 pixels right and 100 down from the top-left of a Chrome window
python main.py 50 100 --window "Chrome"

# 10 right-clicks on a specific app, 0.5 s apart
python main.py 200 300 --count 10 --button right --interval 0.5 --window "My App"
```

Stop at any time with **Ctrl+C**, or move the mouse to **any screen corner** (fail-safe).

---

### `locate.py` — discover coordinates

#### Capture mode (default)
Position your mouse over the target pixel, then press Enter to record it.

```bash
python locate.py          # or: python locate.py capture
```

Output:
```
Press Enter to capture current position...
  Captured: x=842 y=531 rgb=(255,120,30)

python main.py 842 531    # ← ready to paste
```

#### Live mode
Continuously streams the current mouse position and pixel colour as you move.

```bash
python locate.py live
```

#### Window list
Shows every visible window with its screen position and size — useful for picking a `--window` title.

```bash
python locate.py windows
```

Output:
```
Title                                               Left     Top   Width  Height
--------------------------------------------------------------------------------
Google Chrome                                          0       0    1440     900
Terminal                                             200     150     800     500
```

---

## How window targeting works

When `--window "Chrome"` is passed, `main.py` finds the first window whose title contains that string, reads its top-left screen position, and adds it to your x/y values before clicking. This means your coordinates stay valid even if the window moves between runs.

```
Screen (0,0)
  ┌─────────────────────────────┐
  │   Window top-left (wx, wy)  │
  │     ┌───────────────────┐   │
  │     │  your pixel       │   │
  │     │  (wx+x, wy+y) ◀── │── │── click lands here
  │     └───────────────────┘   │
  └─────────────────────────────┘
```

---

## Fail-safe

`pyautogui` will raise an exception and stop the script if the mouse is moved to **any corner of the screen**. This is always active and cannot be disabled.
