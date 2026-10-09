#!/usr/bin/env python3
"""Copy the DCAT-AP 3.0.1 release artifacts from the read-only clone in source/ into data/, named by the pinned commit
(docs/design/sdc-dcat3-ap-PRD.md, section 1). Refuses a clone that is not at the pin.

    python build/snapshot_dcat_ap.py [--source DIR] [--check]
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = "4470b8e"
RELEASE = "3.0.1"
REPO = "DCAT-AP"


def main(check_only: bool, source: Path) -> int:
    repo = source / REPO
    if not repo.is_dir():
        print(f"{REPO}: not cloned (git clone --quiet https://github.com/SEMICeu/DCAT-AP {repo}; git -C {repo} checkout {PIN})")
        return 1
    at = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=7", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if at != PIN:
        print(f"{REPO}: at {at}, pinned {PIN}; re-pinning is a deliberate step (PRD section 1)")
        return 1
    print(f"{REPO}: {PIN} ok")
    if check_only:
        return 0
    rel = repo / "releases" / RELEASE
    out = ROOT / "data" / f"dcat-ap-{RELEASE}-{PIN}"
    out.mkdir(parents=True, exist_ok=True)
    for d in ("shacl", "context"):
        if (out / d).exists():
            shutil.rmtree(out / d)
        shutil.copytree(rel / d, out / d)
    ex = out / "examples"
    if ex.exists():
        shutil.rmtree(ex)
    ex.mkdir()
    for f in (rel / "html" / "examples").iterdir():
        if f.suffix in (".ttl", ".jsonld"):
            shutil.copy2(f, ex / f.name)
    shutil.copy2(rel / "CHANGELOG.md", out / "CHANGELOG.md")
    shutil.copy2(repo / "LICENSE", out / "LICENSE")
    print(f"snapshot: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    src = Path(args[args.index("--source") + 1]) if "--source" in args else ROOT / "source"
    sys.exit(main("--check" in args, src))
