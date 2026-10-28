# Raw profile of the Tohoku files of 現存植生図2024 (before any cutting)

Source: G空間情報センター record `biodic_veg2024`, files downloaded 2026-10-28 (sha256 in data/raw/20261028/MANIFEST.json, kept in the Hugging Face repo).

| item | veg2024bk2a.gpkg | veg2024bk2b.gpkg |
| --- | --- | --- |
| layers | veg2024bk2a (Polygon) | veg2024bk2b (Polygon) |
| rows | 591,487 | 587,145 |
| geometry stored (shapely type id; 3 Polygon, 6 MultiPolygon) | {'6': 591487} | {'6': 587145} |
| CRS | EPSG:6668 (JGD2011) | EPSG:6668 (JGD2011) |
| bbox lon/lat | 139.2468, 36.8364, 141.6215, 39.3362 | 139.6216, 38.6696, 142.1214, 41.5859 |
| invalid geometries | 0 | 0 |
| null / empty geometries | 0 / 0 | 0 / 0 |
| distinct legends (凡例コード x 凡例名) | 221 | 189 |
| codes with more than one name | 0 | 0 |
| NULLs in any attribute | 0 | 0 |
| 作成年度 values | 2000:79732, 2001:13829, 2002:38884, 2003:43126, 2006:55546, 2009:11743, 2013:15979, 2015:86248, 2016:7257, 2017:76175, 2018:47676, 2020:115292 | 2000:26822, 2001:21917, 2003:31232, 2005:13150, 2007:8411, 2008:41938, 2010:26104, 2012:15567, 2013:34266, 2014:78016, 2015:97247, 2016:9291, 2017:9064, 2018:20444, 2020:69099, 2022:84577 |

Columns (all stored as text, 11 attributes plus the GeoPackage fid): 植生区分コード, 大区分コード, 中区分コード, 細区分コード, 凡例コード, 凡例名, 植生自然度, 植生自然度区分, 植生区分, 作成年度, 地域ブロック.

Notes
- The layer is declared Polygon in the GeoPackage but every stored geometry is a MultiPolygon.
- Both files carry 地域ブロック = 2 (Tohoku). Their extents overlap (a: 36.84-39.34 N, b: 38.67-41.59 N), and Akita (about 38.9-40.5 N) can lie in both; this is checked when Akita is cut out.
- The numeric-looking columns (作成年度, 植生自然度) are text in the source and kept as such.
- `legend_all_tohoku_raw.tsv` lists every legend; `legend_matches_tohoku_raw.tsv` lists the 50 rows (33 codes) whose name contains ブナ, ミズナラ, ナラ or コナラ, in the original spelling. The match is by substring, so it also catches イヌブナ and ミヤマナラ, which are other species; nothing was merged.
