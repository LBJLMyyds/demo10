"""Shared paths and dataset metadata for the accessibility data pipeline."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = PROJECT_ROOT / "database"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"

DATABASE_PATH = DATABASE_DIR / "accessibility.sqlite"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
VALIDATION_REPORT_PATH = REPORTS_DIR / "data_validation_report.md"


RAW_DATASETS = [
    {
        "source_id": "enaccess_places",
        "filename": "enaccess_places.csv",
        "description": "Aggregated accessibility place data from the EnAccess Maps export.",
        "license": "Project-provided dataset",
        "origin": "Archived MAST90106 project data",
    },
    {
        "source_id": "enaccess_reviews",
        "filename": "enaccess_reviews.csv",
        "description": "Individual accessibility reviews linked to EnAccess places.",
        "license": "Project-provided dataset",
        "origin": "Archived MAST90106 project data",
    },
    {
        "source_id": "accessible_toilets_15_councils",
        "filename": "accessible_toilets_15_councils.csv",
        "description": "Accessible public toilet records filtered to the target councils.",
        "license": "Public data export, verify before publication",
        "origin": "Archived MAST90106 project data",
    },
    {
        "source_id": "melbourne_public_toilets",
        "filename": "melbourne_public_toilets.csv",
        "description": "City of Melbourne public toilet point dataset.",
        "license": "Public data export, verify before publication",
        "origin": "Archived MAST90106 project data",
    },
    {
        "source_id": "tactile_ground_surface_indicators",
        "filename": "tactile_ground_surface_indicators.csv",
        "description": "City of Melbourne tactile ground surface indicator assets.",
        "license": "Public data export, verify before publication",
        "origin": "Archived MAST90106 project data",
    },
    {
        "source_id": "council_data_reference",
        "filename": "council_overview.csv",
        "description": "Reference council accessibility dataset catalogue from the GitHub repo.",
        "license": "Inherited from reference repository",
        "origin": "https://github.com/HangyuZhao/MAST90106-group-project-accessibility-map",
    },
    {
        "source_id": "mount_alexander_map",
        "filename": "council_data/mount_alexander_map.csv",
        "description": "Reference accessibility points extracted from map images.",
        "license": "Inherited from reference repository",
        "origin": "https://github.com/HangyuZhao/MAST90106-group-project-accessibility-map",
    },
]
