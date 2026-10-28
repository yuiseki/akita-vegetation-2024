"""Constants shared by the scripts of akita-vegetation-2024."""

CKAN_ID = "biodic_veg2024"
CKAN_URL = f"https://www.geospatial.jp/ckan/api/3/action/package_show?id={CKAN_ID}"
PAGE_URL = f"https://www.geospatial.jp/ckan/dataset/{CKAN_ID}"
BIODIC_PAGE_URL = "https://www.biodic.go.jp/kiso/vg/vg_kiso.html"
STORY_URL = (
    "https://pl-moej.gisservice.jp/arcgis/apps/storymaps/stories/a366ce0b9e674e46872baac1ab34eb13"
)
LICENSE_ID = "public-data-license-v1.0"
PDL_URL = "https://www.digital.go.jp/resources/open_data/public_data_license_v1.0"
UA = "Mozilla/5.0 (research; yuiseki)"
# Akita lies in the Tohoku block, which the publisher split into two files, a and b.
TOHOKU_FILES = ["veg2024bk2a.gpkg", "veg2024bk2b.gpkg"]
N03_URL = "https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_05_GML.zip"
N03_PAGE_URL = "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html"
AKITA_PREF_CODE = "05"
