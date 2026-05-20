"""
Configuration for the Data Validation Framework

This module defines the shared paths and constants used across the
CLI runner, Streamlit app, and backend framework. It intentionally
avoids hard‑coded filenames so the system can auto‑discover datasets
and remain flexible as new files are added.

Sections:
- Imports
- Base paths
- Data directories
- Dataset → table name mapping
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from pathlib import Path


# ---------------------------------------------------------------------------
# Base Paths
# ---------------------------------------------------------------------------
# BASE_DATA_PATH is the root folder where all datasets live.
# Both the CLI runner and Streamlit app rely on this shared location.
#
# IMPORTANT:
# - This path is intentionally simple and relative.
# - A future GUI can read from this same location without modification.
# ---------------------------------------------------------------------------

BASE_DATA_PATH = Path("python_data_validator/data")


# ---------------------------------------------------------------------------
# Data Directories
# ---------------------------------------------------------------------------
# These folders contain the actual SQLite files and expected CSV files.
# The application will auto‑discover files inside these directories.
#
# Why this matters:
# - The CLI runner can list available datasets.
# - The Streamlit app can populate dropdowns.
# - A future GUI can show a file‑picker or dataset selector.
# ---------------------------------------------------------------------------

ACTUAL_DIR = BASE_DATA_PATH / "actual"
EXPECTED_DIR = BASE_DATA_PATH / "expected"


# ---------------------------------------------------------------------------
# Dataset → Table Name Mapping
# ---------------------------------------------------------------------------
# TABLE_NAME_MAP allows you to override the table name used for a dataset.
#
# Example:
#   monsters.sqlite       → table "monsters"
#   monsters_bad.sqlite   → table "monsters"
#
# If a dataset name is NOT in this mapping, the system falls back to:
#   table_name = dataset_name
#
# This keeps everything flexible while still supporting special cases.
#
# A future GUI will use this mapping to:
# - Display friendly table names
# - Ensure the validator loads the correct table automatically
# ---------------------------------------------------------------------------

TABLE_NAME_MAP = {
    "monsters": "monsters",
    "monsters_bad": "monsters",
    # Add more dataset → table name mappings here as needed.
}
