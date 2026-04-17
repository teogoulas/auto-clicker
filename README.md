# auto-clicker

Repeatedly click a screen coordinate at a configurable interval. Supports window-relative targeting and interactive pixel discovery — all from a single script.

## Setup

```bash
conda env create -f environment.yml
conda activate auto-clicker
```

> **macOS**: grant Terminal (or your IDE) accessibility permissions in  
> *System Preferences → Privacy & Security → Accessibility*.

---

## Usage

### Default mode — click to detect target

Run the script without coordinates. It waits for you to click anywhere on screen, captures that position (and the window it belongs to), then starts auto-clicking after a 3-second countdown.

```bash
python main.py
python main.py --interval 5 --close-after 30
```

```
Click on your target pixel to set it as the auto-click destination...
Target: abs=(1114,801)  rel=(926,659)  window='Google Chrome'
Starting in 3 seconds... (move mouse to a corner to cancel)
Click at (1114, 801) every 10.0s — until stopped
```

### Explicit coordinates

Skip detection by passing x/y directly.

```bash
python main.py 926 659 --window "Chrome"
python main.py 926 659 --window "Chrome" --close-after 30
python main.py 926 659 --window "Chrome" --window-index 1
```

| Argument | Default | Description |
|---|---|---|
| `x`, `y` | — | Absolute coords, or relative to `--window` (omit to detect via click) |
| `--interval`, `-i` | `10` | Seconds between clicks |
| `--count`, `-n` | `0` | Total clicks (0 = unlimited) |
| `--button`, `-b` | `left` | `left` / `right` / `middle` |
| `--double`, `-d` | off | Double-click |
| `--window`, `-w` | — | Window title substring; makes x/y relative to that window |
| `--window-index` | `0` | Which match to use when multiple windows share the same title |
| `--close-after`, `-c` | — | Close window with Cmd+W after this many **minutes**, then exit |

Stop at any time with **Ctrl+C**, or move the mouse to **any screen corner** (fail-safe).

---

### Discover coordinates — `locate`

#### Capture mode (default)
Hover over your target, press Enter to record. Prints a ready-to-run command.

```bash
python main.py locate
```

```
  abs=(1114,801)  rel=(926,659)  window='Google Chrome'  rgb=(90,110,172)

Ready-to-use commands:
  python main.py 926 659 --window "Google Chrome"
```

#### Live mode
Streams position, window, and pixel colour as you move the mouse.

```bash
python main.py locate live
```

#### Window list
Lists all visible windows with screen coordinates — useful for picking a `--window` value.

```bash
python main.py locate windows
```

---

## How window targeting works

When `--window "Chrome"` is passed, the script finds the matching window, reads its top-left screen position, and adds it to your x/y values before clicking. Coordinates stay valid even if the window moves.

```
Screen (0,0)
  ┌─────────────────────────────┐
  │   Window top-left (wx, wy)  │
  │     ┌───────────────────┐   │
  │     │  your pixel       │   │
  │     │  (wx+x, wy+y) ◀───┼───┼── click lands here
  │     └───────────────────┘   │
  └─────────────────────────────┘
```

---

## Fail-safe

`pyautogui` stops the script if the mouse is moved to **any corner of the screen**. Always active.
