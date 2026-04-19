# auto-clicker

Two tools in one repo:

- **`scraper.py`** — Playwright-based automator for the Aegean College e-learning platform. Logs in, navigates to a course, and cycles through slideshow slides automatically.
- **`main.py`** — General-purpose auto-clicker for repeating mouse clicks at a configurable interval.

## Prerequisites — Install Miniconda

If you don't have `conda` installed, install Miniconda (a minimal conda distribution):

**macOS**
```bash
brew install --cask miniconda
```
Or download the installer manually from https://docs.conda.io/en/latest/miniconda.html, then run:
```bash
bash ~/Downloads/Miniconda3-latest-MacOSX-arm64.sh   # Apple Silicon
# or
bash ~/Downloads/Miniconda3-latest-MacOSX-x86_64.sh  # Intel
```

**Linux**
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
Follow the prompts, then restart your terminal (or run `source ~/.bashrc`).

**Windows**

Download and run the installer from https://docs.conda.io/en/latest/miniconda.html.  
Use **Miniconda3 Windows 64-bit**. During installation, check *"Add Miniconda3 to my PATH"* (or use the **Anaconda Prompt** that gets installed).

---

## Setup

```bash
conda env create -f environment.yml
conda activate auto-clicker
playwright install chromium
```

> **macOS**: grant Terminal (or your IDE) accessibility permissions in  
> *System Preferences → Privacy & Security → Accessibility*.

---

## `scraper.py` — E-learning automator

Logs into `ops.aegeancollege.gr`, navigates to your course, opens a SCORM slideshow, and keeps clicking **Next** on a timer — across multiple login/logout cycles.

**Compatible with macOS, Linux, and Windows.** On macOS the display is kept awake automatically via `caffeinate`. On Linux, `xdg-screensaver` is used if available. On Windows, disable sleep manually via your power settings.

### Usage

```bash
python scraper.py \
  --username YOUR_EMAIL \
  --password YOUR_PASSWORD \
  --section "AI Training" \
  --subsection "Ενότητα 1"
```

| Argument | Default | Description |
|---|---|---|
| `--username` | required | Login e-mail or username |
| `--password` | required | Login password |
| `--section` | required | Section name to expand — case-insensitive substring match |
| `--subsection` | required | Sub-section (activity) to open — case-insensitive substring match |
| `--next-interval` | `30` | Seconds between each **Next** click in the slideshow |
| `--cycle-interval` | `60` | Minutes per cycle before logging out and back in |
| `--cycles` | `4` | Total number of login/logout cycles to run |

### Example

```bash
python scraper.py \
  --username student@example.com \
  --password secret \
  --section "AI Training - Γενικα για Τεχνητή Νοημοσύνη" \
  --subsection "Ενότητα 1" \
  --next-interval 45 \
  --cycle-interval 90 \
  --cycles 6
```

### How it works

1. Opens a Chromium browser window (visible, not headless).
2. Logs into `ops.aegeancollege.gr`.
3. Navigates to `aegean.edu-elearning.gr/my/courses.php` and clicks the matching course card.
4. Finds and expands the matching section, then clicks the matching sub-section.
5. Waits for the SCORM slideshow popup and mutes all audio via JavaScript.
6. Clicks **Next** every `--next-interval` seconds until the cycle time expires.
7. Closes the slideshow, logs out, and repeats for the configured number of cycles.

---

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
