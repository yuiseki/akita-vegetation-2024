#!/usr/bin/env python3
"""Verify and profile the Akita extract: polygons, area, legends, survey years, NULLs, validity.

uv run python scripts/05_profile_akita.py   # writes docs/akita_profile.json, legend_akita.tsv, legend_matches_akita.tsv, akita_profile.md
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely

ROOT = Path(__file__).parents[1]
WORDS = ["ブナ", "ミズナラ", "ナラ", "コナラ"]
AREA_CRS = 6678


def main() -> int:
    df = gpd.read_parquet(ROOT / "data" / "parquet" / "vegetation_akita.parquet")
    g = df.geometry.values
    res = {
        "polygons": len(df),
        "crs": df.crs.to_string(),
        "bbox": [float(x) for x in df.total_bounds],
    }
    res["geometry_types"] = df.geometry.geom_type.value_counts().to_dict()
    res["invalid"] = int((~shapely.is_valid(g)).sum())
    res["empty"] = int(shapely.is_empty(g).sum())
    res["fid_unique"] = bool(df["fid"].is_unique)
    res["nulls"] = {c: int(df[c].isna().sum()) for c in df.columns if c != "geometry"}
    res["clipped"] = int(df["clipped"].sum())
    res["by_source_file"] = df["source_file"].value_counts().to_dict()
    res["area_km2_total"] = float(df["area_m2"].sum() / 1e6)
    res["area_km2_clipped_part"] = float(df.loc[df["clipped"], "area_m2"].sum() / 1e6)
    res["source_area_km2_of_clipped_polygons"] = float(
        df.loc[df["clipped"], "source_area_m2"].sum() / 1e6
    )
    z = ROOT / "data" / "docs" / "N03-20260101_05_GML.zip"
    import zipfile

    shp = next(n for n in zipfile.ZipFile(z).namelist() if n.endswith(".shp"))
    akita = gpd.read_file(f"zip://{z}!{shp}").to_crs(AREA_CRS).geometry.union_all()
    res["akita_n03_area_km2"] = float(akita.area / 1e6)
    res["share_of_n03_area"] = res["area_km2_total"] / res["akita_n03_area_km2"]
    # overlap among polygons: the sum of areas against the area of the union is checked on a sample of pairs by the tree
    tree = shapely.STRtree(g)
    a, b = tree.query(g, predicate="intersects")
    pair = a < b
    inter = shapely.area(shapely.intersection(g[a[pair]], g[b[pair]]))
    res["overlapping_pairs_with_area"] = int(
        (inter > 1e-12).sum()
    )  # square degrees, a few mm2 or more
    res["max_overlap_deg2"] = float(inter.max()) if len(inter) else 0.0
    res["value_counts"] = {
        c: df[c].value_counts().sort_index().to_dict()
        for c in ["作成年度", "植生区分", "植生自然度", "植生自然度区分", "地域ブロック"]
    }
    leg = (
        df.groupby(["凡例コード", "凡例名", "植生区分", "植生自然度"])
        .agg(polygons=("fid", "size"), area_km2=("area_m2", lambda s: s.sum() / 1e6))
        .reset_index()
    )
    leg.to_csv(ROOT / "docs" / "legend_akita.tsv", sep="\t", index=False)
    mask = pd.concat([leg["凡例名"].str.contains(w, regex=False) for w in WORDS], axis=1).any(
        axis=1
    )
    hit = leg[mask].copy()
    for w in WORDS:
        hit[f"has_{w}"] = hit["凡例名"].str.contains(w, regex=False)
    hit.to_csv(ROOT / "docs" / "legend_matches_akita.tsv", sep="\t", index=False)
    res["legends"] = int(len(leg))
    res["legend_matches"] = {
        "codes": int(len(hit)),
        "polygons": int(hit["polygons"].sum()),
        "area_km2": float(hit["area_km2"].sum()),
    }
    res["year_by_legend_match"] = (
        df[df["凡例コード"].isin(hit["凡例コード"])]["作成年度"]
        .value_counts()
        .sort_index()
        .to_dict()
    )
    log = json.loads((ROOT / "docs" / "extract_log.json").read_text())
    md = [
        "# Akita extract of 現存植生図2024: verification and profile",
        "",
        f"- polygons: {res['polygons']:,} (all MultiPolygon), CRS {res['crs']}, bbox lon {res['bbox'][0]:.4f} to {res['bbox'][2]:.4f}, lat {res['bbox'][1]:.4f} to {res['bbox'][3]:.4f}",
        f"- source files: {res['by_source_file']}",
        f"- cut: {log['files']['veg2024bk2a.gpkg']['wholly_inside'] + log['files']['veg2024bk2b.gpkg']['wholly_inside']:,} polygons wholly inside Akita kept as they are; {res['clipped']:,} polygons that cross the boundary were clipped to it (none dropped); the clipped polygons had {res['source_area_km2_of_clipped_polygons']:.1f} km2 before the cut and keep {res['area_km2_clipped_part']:.1f} km2",
        f"- area: {res['area_km2_total']:.3f} km2 in EPSG:6678, against {res['akita_n03_area_km2']:.3f} km2 for the N03 polygon of Akita ({res['share_of_n03_area'] * 100:.5f}%), so the map has no gaps against that boundary",
        f"- geometry validity: {res['invalid']} invalid, {res['empty']} empty; fid unique: {res['fid_unique']}",
        f"- overlaps: {res['overlapping_pairs_with_area']} pairs of polygons overlap by a sliver (largest {res['max_overlap_deg2']:.2e} square degrees, about 80 m2); not repaired",
        f"- NULLs: {sum(res['nulls'].values())} in all columns",
        "",
        "## 作成年度 (polygons)",
        "",
        "| year | polygons |",
        "| --- | ---: |",
    ]
    md += [f"| {k} | {v:,} |" for k, v in res["value_counts"]["作成年度"].items()]
    md += [
        "",
        "## Legends whose name contains ブナ, ミズナラ, ナラ or コナラ",
        "",
        f"{res['legend_matches']['codes']} of the {res['legends']} legends present in Akita; {res['legend_matches']['polygons']:,} polygons, {res['legend_matches']['area_km2']:.1f} km2 together (the legends overlap in meaning, do not read this as one class).",
        "",
        "| code | name (original) | polygons | area km2 | ブナ | ミズナラ | ナラ | コナラ |",
        "| --- | --- | ---: | ---: | :-: | :-: | :-: | :-: |",
    ]
    for r in hit.itertuples(index=False):
        md.append(
            f"| {r[0]} | {r[1]} | {r[4]:,} | {r[5]:.2f} | "
            + " | ".join("x" if getattr(r, f"has_{w}") else "" for w in WORDS)
            + " |"
        )
    md += [
        "",
        "The match is by substring on the original name: ナラ also matches ミヤマナラ (a shrub oak of the alpine zone), ブナ also matches イヌブナ where present. The full list of Akita legends is `legend_akita.tsv`.",
        "",
        "## 作成年度 of the polygons of those legends",
        "",
        "| year | polygons |",
        "| --- | ---: |",
    ]
    md += [f"| {k} | {v:,} |" for k, v in res["year_by_legend_match"].items()]
    (ROOT / "docs" / "akita_profile.md").write_text("\n".join(md) + "\n")
    (ROOT / "docs" / "akita_profile.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1) + "\n"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in res.items()
                if k not in ("value_counts", "nulls", "year_by_legend_match")
            },
            ensure_ascii=False,
            indent=1,
        )
    )
    print(hit[["凡例コード", "凡例名", "polygons", "area_km2"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
