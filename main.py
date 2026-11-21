"""Deliver the front page of Saturday 21 November 2026.

This repository holds one picture, entry.png: a newspaper front page
that sums up the world news of Saturday 21 November 2026. It leads with
Russia's overnight assault on Ukraine — more than 400 drones and 110
missiles, two of them landing in Poland — and continues with the AI
sell-off that pushed the S&P 500 into correction, Bitcoin's fall below
$60,000, the World Court's genocide ruling against Myanmar, Trump's
press conference after the Shenzhen summit, a pancreatic-cancer pill
breakthrough, COP31 running into overtime, an earthquake in Peru, and
the post-Brexit deals signed in Brussels, with shorter briefs below.

The program's whole job is to put that picture, unchanged, at
$MAKEFUN_OUTPUT_DIR/entry.png (falling back to /output/entry.png).
It uses only the standard library, touches no network and reads no
clock, so every run produces exactly the same bytes. The stored
picture is checked before the copy and the copy is checked after it:
a file that is not a whole PNG, is over the 1 MiB cap, or differs from
the stored picture by a single byte fails the run instead of passing
silently.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
SOURCE = REPO_DIR / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SIZE_CAP = 1_048_576  # the competition's 1 MiB limit
# SHA-256 of entry.png as rendered by render_frontpage.py (kept outside
# this repository) and frozen on 21 November 2026. The stored picture
# must match it exactly, so a damaged or swapped entry.png is refused
# rather than delivered.
PINNED_SHA256 = "c06eedbf40d5a2c608e1f4041f07a63f915ff77683179311f52beef4a0fec1e1"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_picture(path: Path, label: str) -> int:
    """Return the byte size of a whole, in-cap PNG, or raise ValueError."""
    size = path.stat().st_size
    if size > SIZE_CAP:
        raise ValueError(f"{label} is {size} bytes, over the 1 MiB cap")
    with path.open("rb") as fh:
        if fh.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise ValueError(f"{label} does not start with the PNG signature")
    return size


def deliver() -> Path:
    check_picture(SOURCE, "stored entry.png")
    if sha256_of(SOURCE) != PINNED_SHA256:
        raise ValueError("stored entry.png does not match the pinned SHA-256")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(SOURCE, target)
    check_picture(target, "written entry.png")
    if sha256_of(target) != sha256_of(SOURCE):
        raise ValueError("written entry.png differs from the stored picture")
    return target


def main() -> int:
    try:
        target = deliver()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr, flush=True)
        return 1
    print(f"delivered {target} ({target.stat().st_size} bytes)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
