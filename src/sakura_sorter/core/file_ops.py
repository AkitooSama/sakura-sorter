from pathlib import Path
import shutil
from sakura_sorter.core.tags import strip
from sakura_sorter.core import history
import traceback

def unique(path: Path) -> Path:
    i = 1
    base = path.stem
    while path.exists():
        path = path.with_name(f"{base}_{i}{path.suffix}")
        i += 1
    return path

def distribute(src: Path, targets: list[Path], clean_name: bool):
    name = strip(src.name) if clean_name else src.name

    written = []
    errors = []

    for folder in targets:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            dst = unique(folder / name)
            shutil.copy2(src, dst)
            written.append(str(dst))
        except Exception as e:
            errors.append(f"{folder}: {e}")

    msg = ""
    all_succeeded = len(written) == len(targets)
    if not all_succeeded and errors:
        msg = "; ".join(errors)

    success = False
    if all_succeeded:
        try:
            src.unlink()
            success = True
        except Exception as e:
            msg = (msg + "; " if msg else "") + f"unlink {src}: {e}"

    try:
        history.log_action(str(src), written, success, msg)
    except Exception:
        traceback.print_exc()

    return {"src": str(src), "destinations": written, "success": success, "message": msg}
