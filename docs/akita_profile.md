# Akita extract of 現存植生図2024: verification and profile

- polygons: 174,576 (all MultiPolygon), CRS EPSG:6668, bbox lon 139.6917 to 140.9954, lat 38.8730 to 40.5111
- source files: {'veg2024bk2b.gpkg': 169196, 'veg2024bk2a.gpkg': 5380}
- cut: 173,114 polygons wholly inside Akita kept as they are; 1,462 polygons that cross the boundary were clipped to it (none dropped); the clipped polygons had 3112.5 km2 before the cut and keep 828.8 km2
- area: 11635.884 km2 in EPSG:6678, against 11635.886 km2 for the N03 polygon of Akita (99.99999%), so the map has no gaps against that boundary
- geometry validity: 0 invalid, 0 empty; fid unique: True
- overlaps: 123 pairs of polygons overlap by a sliver (largest 8.07e-09 square degrees, about 80 m2); not repaired
- NULLs: 0 in all columns

## 作成年度 (polygons)

| year | polygons |
| --- | ---: |
| 2001 | 21,916 |
| 2003 | 6 |
| 2007 | 8,411 |
| 2010 | 20,482 |
| 2012 | 2,920 |
| 2015 | 6,966 |
| 2016 | 3,534 |
| 2017 | 2,470 |
| 2020 | 68,954 |
| 2022 | 38,917 |

## Legends whose name contains ブナ, ミズナラ, ナラ or コナラ

11 of the 134 legends present in Akita; 36,259 polygons, 4168.0 km2 together (the legends overlap in meaning, do not read this as one class).

| code | name (original) | polygons | area km2 | ブナ | ミズナラ | ナラ | コナラ |
| --- | --- | ---: | ---: | :-: | :-: | :-: | :-: |
| 110100 | チシマザサ－ブナ群団 | 2,136 | 1190.88 | x |  |  |  |
| 110103 | スギ－ブナ群落 | 812 | 115.88 | x |  |  |  |
| 110501 | ホツツジ－ミズナラ群集 | 188 | 4.63 |  | x | x |  |
| 190100 | ウラジロヨウラク－ミヤマナラ群団 | 689 | 30.07 |  |  | x |  |
| 220100 | ブナ－ミズナラ群落 | 4,004 | 535.11 | x | x | x |  |
| 220101 | スギ－ミズナラ群落 | 306 | 18.43 |  | x | x |  |
| 220103 | オオバクロモジ－ミズナラ群集 | 9,411 | 1296.31 |  | x | x |  |
| 220104 | ブナ二次林 | 114 | 12.76 | x |  |  |  |
| 220500 | コナラ群落（V） | 502 | 25.54 |  |  | x | x |
| 220501 | オクチョウジザクラ－コナラ群集 | 18,039 | 934.74 |  |  | x | x |
| 221100 | ミズナラ群落（V） | 58 | 3.69 |  | x | x |  |

The match is by substring on the original name: ナラ also matches ミヤマナラ (a shrub oak of the alpine zone), ブナ also matches イヌブナ where present. The full list of Akita legends is `legend_akita.tsv`.

## 作成年度 of the polygons of those legends

| year | polygons |
| --- | ---: |
| 2001 | 6,156 |
| 2003 | 2 |
| 2007 | 1,298 |
| 2010 | 4,146 |
| 2012 | 756 |
| 2015 | 1,410 |
| 2016 | 806 |
| 2017 | 572 |
| 2020 | 12,982 |
| 2022 | 8,131 |
