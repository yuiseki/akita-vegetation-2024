# akita-vegetation-2024

Akita Prefecture extract of 現存植生図2024 (Biodiversity Center of Japan, Ministry of the Environment),
frozen on Hugging Face as `yuiseki/akita-vegetation-2024`. Survey: https://github.com/yuiseki/akita-beech-oak-sources

Scripts run in order (`uv run python scripts/NN_*.py`); `data/` is not in git.

1. `01_download.py` the two Tohoku GeoPackages from G空間情報センター and the Akita boundary (cutter only)
2. `02_profile_raw.py`, `03_legend_match.py` raw profile; results in `docs/`
3. `04_extract_akita.py`, `05_profile_akita.py` cut Akita and profile it
4. `06_card.py` card, licence, provenance; `07_verify.py` second-engine check against the source
5. `src/publish.py --push` upload in one commit; `08_verify_hub.py` read back at the fixed revision (`docs/revision.md`)
