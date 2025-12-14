import re

TAG_RE = re.compile(r"^\[(.*?)\]")

def parse(filename: str) -> list[str]:
    m = TAG_RE.match(filename)
    if not m:
        return []
    return [t.strip().lower() for t in m.group(1).split(",")]

def strip(filename: str) -> str:
    return TAG_RE.sub("", filename)
