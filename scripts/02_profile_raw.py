#!/usr/bin/env python3
"""Profile the raw Tohoku files as they are (no cutting): layers, rows, geometry type, CRS, bbox,
invalid geometries, columns, legend values, survey years, nulls.

    uv run python scripts/02_profile_raw.py   # writes docs/raw_profile.json and docs/raw_profile.md
"""

import json
import sys
from pathlib import Path

import numpy as np
import pyogrio
import shapely
import veg

ROOT = Path(__file__).parents[1]


def profile(path: Path) -> dict:
    layers = pyogrio.list_layers(path)
    out = {"file": path.name, "layers": [[str(a), str(b)] for a, b in layers]}
    layer = str(layers[0][0])
    info = pyogrio.read_info(path, layer=layer)
    out |= {"rows": int(info["features"]), "crs": str(info["crs"]), "geometry_type": info["geometry_type"],
            "fields": [str(f) for f in info["fields"]], "dtypes": [str(d) for d in info["dtypes"]]}  # fmt: skip
    attrs = pyogrio.read_dataframe(path, layer=layer, read_geometry=False)
    out["nulls"] = {c: int(attrs[c].isna().sum()) for c in attrs.columns}
    out["empty_strings"] = {
        c: int((attrs[c] == "").sum()) for c in attrs.columns if attrs[c].dtype == object
    }
    for col in ("作成年度", "植生区分コード", "植生区分", "地域ブロック", "植生自然度"):
        out[f"value_counts:{col}"] = {
            str(k): int(v) for k, v in attrs[col].value_counts(dropna=False).sort_index().items()
        }
    leg = attrs.groupby(["凡例コード", "凡例名"], dropna=False).size().reset_index(name="n")
    out["legend_n"] = int(len(leg))
    out["legend_codes_with_several_names"] = sorted(
        leg.groupby("凡例コード")
        .filter(lambda g: len(g) > 1)["凡例コード"]
        .astype(str)
        .unique()
        .tolist()
    )
    out["fid_unique"] = bool(attrs["fid"].is_unique) if "fid" in attrs.columns else None
    geo = pyogrio.read_dataframe(path, layer=layer, columns=[])
    g = geo.geometry.values
    out["bbox"] = [float(x) for x in geo.total_bounds]
    out["geometry_types"] = {
        str(k): int(v)
        for k, v in zip(*np.unique(shapely.get_type_id(g), return_counts=True), strict=True)
    }
    out["null_geometry"] = int(shapely.is_missing(g).sum())
    out["empty_geometry"] = int(shapely.is_empty(g).sum())
    out["invalid_geometry"] = int((~shapely.is_valid(g)).sum())
    return out


def main() -> int:
    run = sorted((ROOT / "data" / "raw").glob("*/MANIFEST.json"))[-1].parent
    res = {name: profile(run / name) for name in veg.TOHOKU_FILES}
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "raw_profile.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1) + "\n"
    )
    for name, p in res.items():
        print(
            name,
            p["rows"],
            p["crs"][:40],
            p["geometry_types"],
            "invalid",
            p["invalid_geometry"],
            "legends",
            p["legend_n"],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
