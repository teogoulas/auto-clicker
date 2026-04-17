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

### Discover coordinates — `locate`

#### Capture mode (default)
Hover over your target, press Enter to record. Prints a ready-to-run command.

```bash
python main.py locate
```

```
Press Enter to capture current position...
  abs=(1114,801)  rel=(926,659)  window='Google Chrome'  rgb=(90,110,172)

Ready-to-use commands:
  python main.py click 926 659 --window "Google Chrome"
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

### Click — `click`

```
python main.py click <x> <y> [options]
```

| Argument | Default | Description |
|---|---|---|
| `x`, `y` | required | Absolute coords, or relative to `--window` |
| `--interval`, `-i` | `10` | Seconds between clicks |
| `--count`, `-n` | `0` | Total clicks (0 = unlimited) |
| `--button`, `-b` | `left` | `left` / `right` / `middle` |
| `--double`, `-d` | off | Double-click |
| `--window`, `-w` | — | Window title substring; makes x/y relative to that window |
| `--window-index` | `0` | Which match to use when multiple windows share the same title |
| `--close-after`, `-c` | — | Close window with Cmd+W after this many **minutes**, then exit |

**Examples**

```bash
# Click at absolute coords every 10 s (default interval)
python main.py click 960 540

# Click relative to a Chrome window, close it after 30 minutes
python main.py click 926 659 --window "Chrome" --close-after 30

# 10 right-clicks 0.5 s apart
python main.py click 200 300 --count 10 --button right --interval 0.5

# Target the second matching Chrome window
python main.py click 926 659 --window "Chrome" --window-index 1
```

Stop at any time with **Ctrl+C**, or move the mouse to **any screen corner** (fail-safe).

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
