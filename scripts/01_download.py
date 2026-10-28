#!/usr/bin/env python3
"""Download the Tohoku block of 現存植生図2024 and the Akita boundary (the cutter) with checksums.

    uv run python scripts/01_download.py

The record on G空間情報センター is read first and the run stops if its licence is no longer
public-data-license-v1.0. The files are fetched with curl (resumable) from the signed S3 link
that the record's download URL redirects to.
"""

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

import veg

ROOT = Path(__file__).parents[1]


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": veg.UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def probe(url: str) -> tuple[str, dict]:
    """Resolve the redirect to the signed link and read the headers of a one-byte range."""
    out = subprocess.run(
        ["curl", "-sS", "-L", "-A", veg.UA, "-r", "0-0", "-D", "-", "-o", "/dev/null",
         "-w", "\n@@%{url_effective}", url],
        check=True, capture_output=True, text=True,
    ).stdout.replace("\r", "")  # fmt: skip
    final = out.rsplit("@@", 1)[1].strip()
    last = [h for h in out.split("\n\n") if h.startswith("HTTP/")][-1]
    pick = {}
    for line in last.splitlines()[1:]:
        k, _, v = line.partition(":")
        if k.lower() in ("etag", "last-modified", "content-range"):
            pick[k.lower()] = v.strip()
    return final, pick


def curl(url: str, dest: Path, connections: int = 8) -> dict:
    """Fetch url into dest. The host serves about 100 KB/s per connection, so a few ranged
    connections are used (aria2c, resumable); the signed link lives one hour, so it is
    resolved again whenever a round ends before the file is whole."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    head = {}
    for _ in range(20):
        final, head = probe(url)
        total = int(head["content-range"].rsplit("/", 1)[1]) if "content-range" in head else None
        if (
            dest.exists()
            and total
            and dest.stat().st_size == total
            and not dest.with_name(dest.name + ".aria2").exists()
        ):
            return head
        subprocess.run(["aria2c", "-c", "-x", str(connections), "-s", str(connections), "-k", "4M",
                        "--user-agent", veg.UA, "--summary-interval=60", "--console-log-level=warn",
                        "-d", str(dest.parent), "-o", dest.name, final], check=False)  # fmt: skip
    raise SystemExit(f"could not fetch {url}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 24):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    run = date.today().strftime("%Y%m%d")
    out = ROOT / "data" / "raw" / run
    out.mkdir(parents=True, exist_ok=True)
    record = json.loads(get(veg.CKAN_URL))["result"]
    if record["license_id"] != veg.LICENSE_ID:
        raise SystemExit(f"the licence of the record changed: {record['license_id']}")
    keep = ("id", "name", "title", "license_id", "license_title", "license_url", "metadata_created",
            "metadata_modified", "author", "maintainer", "notes")  # fmt: skip
    meta = {k: record.get(k) for k in keep}
    meta["organization"] = record["organization"]["title"]
    meta["resources"] = [{k: r.get(k) for k in ("name", "format", "url", "size", "last_modified")}
                         for r in record["resources"]]  # fmt: skip
    (out / "ckan_record.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n")
    manifest = {"run": run, "record": veg.PAGE_URL, "files": {}}
    by_name = {r["url"].rsplit("/", 1)[1]: r for r in record["resources"] if r["format"] == "gpkg"}
    for name in veg.TOHOKU_FILES:
        r = by_name[name]
        head = curl(r["url"], out / name)
        size = (out / name).stat().st_size
        if size != int(r["size"]):
            raise SystemExit(f"{name}: {size} bytes, the record says {r['size']}")
        manifest["files"][name] = {"url": r["url"], "size": size, "sha256": sha256(out / name),
                                   "record_last_modified": r["last_modified"], "http": head}  # fmt: skip
        print(name, size)
    docs = ROOT / "data" / "docs"
    head = curl(veg.N03_URL, docs / "N03-20260101_05_GML.zip")
    manifest["files"]["N03-20260101_05_GML.zip"] = {
        "url": veg.N03_URL, "size": (docs / "N03-20260101_05_GML.zip").stat().st_size,
        "sha256": sha256(docs / "N03-20260101_05_GML.zip"), "http": head, "role": "cutter only"}  # fmt: skip
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n")
    print("wrote", out / "MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
