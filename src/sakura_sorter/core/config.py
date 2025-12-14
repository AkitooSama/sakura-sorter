from pathlib import Path
import os
import platform
from importlib.resources import files

APP_NAME = "sakura-sorter"

if platform.system() == "Windows":
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    icon_name = "icon.ico"
else:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    icon_name = "icon.png"

CONFIG_DIR = base / APP_NAME
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

ASSET_DIR = files("sakura_sorter") / "assets"

THEME_DIR = ASSET_DIR / "themes"
ICON_DIR = ASSET_DIR / "icons"
SOUND_DIR = ASSET_DIR / "sounds"
FONT_DIR = ASSET_DIR / "fonts"

ICON = ICON_DIR / icon_name
SETTINGS_FILE = CONFIG_DIR / "settings.json"
