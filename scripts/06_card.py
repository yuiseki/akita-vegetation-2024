#!/usr/bin/env python3
"""Write data/README.md (the dataset card), data/LICENSE and data/provenance.yaml from the measured docs.

uv run python scripts/06_card.py
"""

import json
from pathlib import Path

import pandas as pd
import veg

ROOT = Path(__file__).parents[1]
DATA = ROOT / "data"
REPO = "akita-vegetation-2024"

ATTRIBUTION_JA = (
    f"出典：「現存植生図2024」（環境省生物多様性センター）（{veg.PAGE_URL}）、PDL1.0（{veg.PDL_URL}）。"
    "環境省生物多様性センターのデータを、yuiseki が秋田県境で切り出し、県境上のポリゴンを切り取り、"
    "GeoParquet に変換して作成した加工物であり、環境省が作成した未加工のデータではない。（取得日 {date}）"
)

CARD = """---
license: other
license_name: pdl-1.0
license_link: {pdl}
language:
- ja
tags:
- vegetation
- japan
- akita
- geospatial
- geoparquet
size_categories:
- 100K<n<1M
configs:
- config_name: default
  data_files: parquet/vegetation_akita.parquet
---

# 現存植生図2024 秋田県 (akita-vegetation-2024)

環境省生物多様性センターの「現存植生図2024」のうち、秋田県の部分を切り出して固定した GeoParquet です。
分析やモデルは含みません。原データの属性と意味を保持しています。

An Akita Prefecture extract of 現存植生図2024 (Ministry of the Environment, Biodiversity Center of Japan; 1/25,000
vegetation survey, survey years 2001 to 2022 in Akita), frozen as GeoParquet. Original attributes are kept; nothing
is merged into classes of my own.

## Source and licence

- Source: 現存植生図2024, 環境省 自然環境局 生物多様性センター. Bulk download used: the Tohoku block, `veg2024bk2a.gpkg`
  and `veg2024bk2b.gpkg`, from the dataset record on G空間情報センター ({page}), the download that the Biodic page
  ({biodic}) and the 現存植生図2024 information site ({story}) point to.
- Retrieved {date}. The record has no version field; it was created 2026-01-23 and its metadata modified {modified};
  the two files carry `Last-Modified` {lm_a} and {lm_b} on the server (the record lists 2026-04-14).
  sha256 of the two source files are in `raw/{run}/MANIFEST.json`.
- Licence: 公共データ利用規約 第1.0版 (PDL1.0), as stated on the record (`public-data-license-v1.0`). PDL1.0 is
  compatible with CC BY 4.0. The conditions that apply: cite the source, and say that the data were edited and by
  whom, without presenting the result as an unprocessed State product. The Biodiversity Center names two cautions: do
  not infringe third-party rights, and legal limits such as the Survey Act where a GSI map is inside the content; none
  is stated for this data, and whether the base map of the survey carries such limits is not stated either.
- Attribution to use: {attribution}
- Cutter: the polygon of Akita in 国土数値情報 行政区域 (N03, 2026-01-01; MLIT), used only to cut and not republished.

## Files

| path | content |
| --- | --- |
| `parquet/vegetation_akita.parquet` | the data, {rows:,} MultiPolygons, GeoParquet, EPSG:6668 (JGD2011), zstd |
| `docs/legend_akita.tsv` | the {legends} legends present in Akita: code, name, 植生区分, 植生自然度, polygons, area |
| `docs/legend_matches_akita.tsv` | the legends whose name contains ブナ, ミズナラ, ナラ or コナラ |
| `docs/akita_profile.md`, `docs/akita_profile.json` | the verification and profile of this extract |
| `docs/raw_profile.md`, `docs/raw_profile.json` | the same for the two Tohoku files before the cut |
| `docs/extract_log.json` | counts of the cut |
| `raw/{run}/MANIFEST.json`, `raw/{run}/ckan_record.json` | source files with sha256, HTTP headers and the record |

## Columns and their correspondence to the source

The source layer has 11 attributes, all text; they keep their names and values. The GeoPackage `fid` is the key of
the polygon over all Japan.

| column here | source | note |
| --- | --- | --- |
| `fid` | GeoPackage fid | unique over Japan; the key back to the source |
| `植生区分コード`, `大区分コード`, `中区分コード`, `細区分コード` | same names | text |
| `凡例コード` | same | text, 6 digits = 大区分 + 中区分 + 細区分 |
| `凡例名` | same | the community name by plant-sociological classification, original spelling (876 legends in Japan) |
| `植生自然度`, `植生自然度区分`, `植生区分` | same | text |
| `作成年度` | same | text, year the polygon was made |
| `地域ブロック` | same | text, 2 = Tohoku |
| `source_file` | added | `veg2024bk2a.gpkg` or `veg2024bk2b.gpkg` |
| `clipped` | added | true when the polygon crossed the Akita boundary and was cut to it |
| `source_area_m2` | added | area of the polygon before the cut, in EPSG:6678 |
| `area_m2` | added | area of the stored polygon, in EPSG:6678 (JGD2011 / Plane Rectangular CS X) |
| `geometry` | geom | MultiPolygon (the GeoPackage layer is declared Polygon but stores MultiPolygons) |

## How Akita was cut

1. Polygons of the two Tohoku files that intersect the N03 polygon of Akita were selected (both files hold parts of Akita:
   {n_a:,} polygons from `bk2a` and {n_b:,} from `bk2b`).
2. {inside:,} polygons lie wholly inside and are kept as they are.
3. {clipped:,} polygons cross the boundary and are clipped to it (their area before the cut was {src_clip:.1f} km2, after the
   cut {after_clip:.1f} km2); `clipped` marks them and `source_area_m2` keeps the original area. None disappeared in the cut.
4. The N03 boundary is an administrative boundary and not the coast line of the vegetation map. The vegetation polygons
   fill the N03 polygon almost completely ({share:.5f}% of its area), so the cut did not leave gaps.

## What is in it

- {rows:,} polygons, {area:.1f} km2, no NULL in any column, {invalid} invalid and {empty} empty geometries.
- 作成年度 (polygons): {years}
- {legends} legends are present. {m_codes} of them contain ブナ, ミズナラ, ナラ or コナラ in the name ({m_polys:,} polygons;
  the legends overlap in meaning, so the areas are not to be added as one class):

{match_table}

The match is by substring on the original name. ナラ also matches ミヤマナラ (190100), which is not ミズナラ or コナラ.
A polygon is one community; the legend does not give the share of a species.

## Cautions

- Polygons were surveyed in different years (see 作成年度); the extract is not a snapshot of one year.
- {pairs} pairs of polygons overlap by slivers (the largest about 80 m2); they are kept as in the source, not repaired.
- The polygons that were cut at the boundary have edges that come from the N03 boundary, not from the survey.
- All numeric-looking attributes are text, as in the source.
- The source data may change on the publisher's side; this is the copy retrieved on {date}.

## Verification

`scripts/07_verify.py` reads the source files again, selects Akita with a second engine (DuckDB spatial), and checks
that the same fids are kept, that the 11 attributes are equal for every polygon, that unclipped geometries are
byte-equal to the source, and that clipped ones are inside the boundary and no larger than the source. After the
upload, `scripts/08_verify_hub.py` reads this repository back at a fixed revision and compares it with the local copy.
The revision is recorded in `docs/revision.md` of the GitHub repository ({github}).

Reproduce: `uv run python scripts/01_download.py`, then `02` to `08` in order.
"""


def main() -> None:
    run = sorted((DATA / "raw").glob("*/MANIFEST.json"))[-1].parent
    man = json.loads((run / "MANIFEST.json").read_text())
    rec = json.loads((run / "ckan_record.json").read_text())
    prof = json.loads((ROOT / "docs" / "akita_profile.json").read_text())
    log = json.loads((ROOT / "docs" / "extract_log.json").read_text())
    hit = pd.read_csv(
        ROOT / "docs" / "legend_matches_akita.tsv", sep="\t", dtype={"凡例コード": str}
    )
    date = f"{run.name[:4]}-{run.name[4:6]}-{run.name[6:]}"
    rows = ["| 凡例コード | 凡例名 | polygons | area km2 |", "| --- | --- | ---: | ---: |"]
    rows += [
        f"| {r.凡例コード} | {r.凡例名} | {r.polygons:,} | {r.area_km2:.2f} |"
        for r in hit.itertuples()
    ]
    f = log["files"]
    years = ", ".join(f"{k}: {v:,}" for k, v in prof["value_counts"]["作成年度"].items())
    lm = lambda n: man["files"][n]["http"]["last-modified"]  # noqa: E731
    attribution = veg_attr = ATTRIBUTION_JA.format(date=date)
    card = CARD.format(
        pdl=veg.PDL_URL, page=veg.PAGE_URL, biodic=veg.BIODIC_PAGE_URL, story=veg.STORY_URL, date=date, run=run.name,
        modified=rec["metadata_modified"][:10], lm_a=lm("veg2024bk2a.gpkg"), lm_b=lm("veg2024bk2b.gpkg"),
        attribution=attribution, rows=prof["polygons"], legends=prof["legends"],
        n_a=f["veg2024bk2a.gpkg"]["kept"], n_b=f["veg2024bk2b.gpkg"]["kept"],
        inside=f["veg2024bk2a.gpkg"]["wholly_inside"] + f["veg2024bk2b.gpkg"]["wholly_inside"],
        clipped=prof["clipped"], src_clip=prof["source_area_km2_of_clipped_polygons"],
        after_clip=prof["area_km2_clipped_part"], share=prof["share_of_n03_area"] * 100, area=prof["area_km2_total"],
        invalid=prof["invalid"], empty=prof["empty"], years=years, m_codes=prof["legend_matches"]["codes"],
        m_polys=prof["legend_matches"]["polygons"], match_table="\n".join(rows),
        pairs=prof["overlapping_pairs_with_area"], github="https://github.com/yuiseki/akita-vegetation-2024",
    )  # fmt: skip
    del veg_attr
    (DATA / "README.md").write_text(card, encoding="utf-8")
    (DATA / "LICENSE").write_text(
        "公共データ利用規約（第1.0版）PDL1.0 (" + veg.PDL_URL + ")\n\n"
        "The data are 現存植生図2024 of the Biodiversity Center of Japan (Ministry of the Environment), published under PDL1.0,\n"
        "which is compatible with CC BY 4.0. They were processed as described in README.md.\n\n"
        + attribution
        + "\n",
        encoding="utf-8",
    )
    (DATA / "provenance.yaml").write_text(
        f"source: 現存植生図2024 (環境省生物多様性センター)\nurl: {veg.PAGE_URL}\nlicense: PDL1.0\n"
        f"retrieved: {date}\nrecord_metadata_modified: {rec['metadata_modified']}\n"
        f"files:\n"
        + "".join(
            f"  - {n}: {v['sha256']}\n" for n, v in man["files"].items() if n.endswith(".gpkg")
        )
        + f"cutter: {veg.N03_URL}\nrows: {prof['polygons']}\n",
        encoding="utf-8",
    )
    print("wrote card, LICENSE, provenance.yaml")


if __name__ == "__main__":
    main()
