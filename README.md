# akita-vegetation-2024

Akita Prefecture extract of 現存植生図2024 (Biodiversity Center of Japan, Ministry of the Environment),
frozen on Hugging Face as `yuiseki/akita-vegetation-2024`. Survey: https://github.com/yuiseki/akita-beech-oak-sources

Scripts run in order (`uv run python scripts/NN_*.py`); `data/` is not in git.

1. `01_download.py` the two Tohoku GeoPackages from G空間情報センター and the Akita boundary (cutter only)
2. `02_profile_raw.py`, `03_legend_match.py` raw profile; results in `docs/`
