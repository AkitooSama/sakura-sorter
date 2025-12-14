<p align="center">
  <img src="app.png" alt="Sakura Sorter" width="900">
</p>

<h1 align="center">Sakura Sorter</h1>

<p align="center">
  Minimal • Fast • Tag‑based File Sorter
</p>

---

## Concept

Sakura Sorter works on **prefix tags**, not filenames or extensions.

You decide destinations using **short tags** inside square brackets at the start of a filename.

Example download:

```
[gw]nature.png
```

- `gw` → green wallpapers folder
- file is moved automatically after appearing in the watch directory

---

## Multiple Destinations

You can route a file to **multiple folders** by adding multiple tags:

```
[gw,n]nature.png
```

This file will be copied or moved to:

- Green Wallpapers
- Nature

Order does not matter.

Whitespace is ignored.

---

## Rule System

Rules map **short tags → folders**.

Example:

| Tag | Destination |
|----|-------------|
| gw | ~/Pictures/Wallpapers/Green |
| n  | ~/Pictures/Nature |

Rules are editable live from the UI.

---

## Filename Rules

- Tags **must** be the first part of the filename
- Tags **must** be inside `[]`
- Tags are comma‑separated
- Case‑insensitive

Valid:
```
[gw]file.png
[gw] file.png
[gw,n]file.png
[gw, n]file.png
[GW,N]file.png
```

Invalid:
```
gw_file.png
[file][gw].png
```

---

## History

- Massive history stored in SQLite
- UI displays latest 200 entries
- Search scans the entire database
- Filter by success / failure
- Inspect full JSON entry
- Delete individual entries or clear all

---

## Themes

- YAML‑based theming
- Hot‑reloadable
- Minimal nature‑inspired palettes
- No hardcoded UI colors

Themes live in:

```
assets/themes/
```

---

## System Tray

- App runs silently in background
- Restore or quit from tray
- Optional notifications

---

## Tech Stack

- Python
- PyQt6
- watchdog
- SQLite
- YAML

---

## Running the Project

### Requirements
- Python 3.10+
- `uv` package manager

---

### Steps

1. **Download the source code**
   - Download or clone the repository
   - Extract it to any directory

2. **Enter the project folder**
   ```bash
   cd sakura-sorter
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Install the app in editable mode**
   ```bash
   python -m pip install -e .
   ```

5. **Run Sakura Sorter**
   ```bash
   sakura-sorter
   ```

That’s it. The UI will launch and stay resident in the system tray when closed.

---

## License

MIT License  
See `LICENSE` for details.
