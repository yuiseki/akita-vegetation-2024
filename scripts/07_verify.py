#!/usr/bin/env python3
"""Check the Akita extract against the source files with a second engine (DuckDB spatial).

uv run python scripts/07_verify.py   # writes docs/verify_local.json, exits 1 on any difference
"""

import json
import sys
from pathlib import Path

import duckdb
import veg

ROOT = Path(__file__).parents[1]
ATTRS = ["植生区分コード", "大区分コード", "中区分コード", "細区分コード", "凡例コード", "凡例名",
         "植生自然度", "植生自然度区分", "植生区分", "作成年度", "地域ブロック"]  # fmt: skip


def main() -> int:
    run = sorted((ROOT / "data" / "raw").glob("*/MANIFEST.json"))[-1].parent
    z = ROOT / "data" / "docs" / "N03-20260101_05_GML.zip"
    pq = ROOT / "data" / "parquet" / "vegetation_akita.parquet"
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    shp = next(n for n in __import__("zipfile").ZipFile(z).namelist() if n.endswith(".shp"))
    con.execute(
        f"create table akita as select ST_Union_Agg(geom) g from ST_Read('/vsizip/{z}/{shp}')"
    )
    src = " union all ".join(
        f"select '{n}' source_file, * from ST_Read('{run / n}')" for n in veg.TOHOKU_FILES
    )
    con.execute(f"create table src as {src}")
    con.execute(f"create table mine as select * from read_parquet('{pq}')")
    res = {}
    q = lambda sql: con.execute(sql).fetchone()[0]  # noqa: E731
    res["source_rows"] = q("select count(*) from src")
    res["rows"] = q("select count(*) from mine")
    res["fid_unique"] = q("select count(distinct fid) = count(*) from mine")
    # route 2: select Akita again with DuckDB
    con.execute(
        "create table sel as select s.fid, s.source_file from src s, akita a where ST_Intersects(s.geom, a.g) and ST_Area(ST_Intersection(s.geom, a.g)) > 0"
    )
    res["reselected"] = q("select count(*) from sel")
    res["only_in_reselected"] = q(
        "select count(*) from sel where fid not in (select fid from mine)"
    )
    res["only_in_mine"] = q("select count(*) from mine where fid not in (select fid from sel)")
    res["source_file_differs"] = q(
        "select count(*) from mine m join sel s using (fid) where m.source_file <> s.source_file"
    )
    cond = " or ".join(f'm."{c}" is distinct from s."{c}"' for c in ATTRS)
    res["attribute_differences"] = q(
        f"select count(*) from mine m join src s using (fid) where {cond}"
    )
    res["unclipped_geometry_not_equal"] = q(
        "select count(*) from mine m join src s using (fid) where not m.clipped and not ST_Equals(m.geometry, s.geom)"
    )
    res["unclipped_wkb_not_identical"] = q(
        "select count(*) from mine m join src s using (fid) where not m.clipped and ST_AsWKB(m.geometry) <> ST_AsWKB(s.geom)"
    )
    res["clipped_outside_boundary"] = q(
        "select count(*) from mine m, akita a where m.clipped and ST_Area(ST_Difference(m.geometry, a.g)) > 1e-12"
    )
    res["clipped_not_equal_to_intersection"] = q(
        "select count(*) from mine m join src s using (fid), akita a where m.clipped and abs(ST_Area(m.geometry) - ST_Area(ST_Intersection(s.geom, a.g))) > 1e-12"
    )
    res["clipped_larger_than_source"] = q(
        "select count(*) from mine m join src s using (fid) where m.clipped and ST_Area(m.geometry) > ST_Area(s.geom) + 1e-12"
    )
    res["invalid"] = q("select count(*) from mine where not ST_IsValid(geometry)")
    res["clipped_rows"] = q("select count(*) from mine where clipped")
    res["unclipped_but_crossing"] = q(
        "select count(*) from mine m, akita a where not m.clipped and not ST_Contains(a.g, m.geometry)"
    )
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "verify_local.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    bad = {
        k: v
        for k, v in res.items()
        if k
        in (
            "only_in_reselected",
            "only_in_mine",
            "source_file_differs",
            "attribute_differences",
            "unclipped_geometry_not_equal",
            "clipped_outside_boundary",
            "clipped_not_equal_to_intersection",
            "clipped_larger_than_source",
            "invalid",
            "unclipped_but_crossing",
        )
        and v
    }
    if res["reselected"] != res["rows"] or not res["fid_unique"] or bad:
        print("DIFFERENCES:", bad, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
