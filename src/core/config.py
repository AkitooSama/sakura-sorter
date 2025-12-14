from pathlib import Path
import os
import platform

APP_NAME = "sakura-sorter"

if platform.system() == "Windows":
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    icon = "icon.ico"
else:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    icon = "icon.png"
    
CONFIG_DIR = base / APP_NAME
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

ASSET_DIR = Path(__file__).parent.parent.parent / "assets"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
THEME_DIR = ASSET_DIR / "themes"
ICON_DIR = ASSET_DIR / "icons"
ICON = ICON_DIR / icon
SOUND_DIR = ASSET_DIR / "sounds"
FONT_DIR = ASSET_DIR / "fonts"
