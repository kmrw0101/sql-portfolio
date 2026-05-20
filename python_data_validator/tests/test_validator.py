"""
Test: Unified Dataset Validation
--------------------------------
This test mirrors the full workflow used by the CLI runner and Streamlit app:

- Discover datasets automatically
- Select a dataset (first one for testing)
- Load expected CSV + actual SQLite
- Apply TABLE_NAME_MAP for table naming
- Run Validator
- Print developer‑friendly summary (via print_summary from conftest.py)
- Assert PASS or FAIL

This ensures the test suite stays aligned with the application architecture.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from .conftest import print_summary
from python_data_validator.framework.data_loader import DataLoader
from python_data_validator.framework.validators import Validator
from python_data_validator.framework.config import (
    BASE_DATA_PATH,
    ACTUAL_DIR,
    EXPECTED_DIR,
    TABLE_NAME_MAP,
)

# NOTE:
# print_summary is NOT imported here.
# Pytest automatically loads it from conftest.py.


# ---------------------------------------------------------------------------
# Dataset Discovery (same logic as CLI + Streamlit)
# ---------------------------------------------------------------------------

def infer_dataset_name(path):
    stem = path.stem
    return stem.split("_", 1)[0] if "_" in stem else stem


def discover_datasets():
    datasets = {}

    # Actual SQLite files
    for db_path in ACTUAL_DIR.glob("*.sqlite"):
        ds = infer_dataset_name(db_path)
        datasets.setdefault(ds, {"actual": [], "expected": []})
        datasets[ds]["actual"].append(db_path)

    # Expected CSV files
    for csv_path in EXPECTED_DIR.glob("*.csv"):
        ds = infer_dataset_name(csv_path)
        datasets.setdefault(ds, {"actual": [], "expected": []})
        datasets[ds]["expected"].append(csv_path)

    return datasets


# ---------------------------------------------------------------------------
# Test: Unified Dataset Validation
# ---------------------------------------------------------------------------

def test_dataset_validation():
    """
    Full end‑to‑end validation test using the same workflow as the CLI runner.
    """

    # -----------------------------
    # Discover datasets
    # -----------------------------
    datasets = discover_datasets()
    assert datasets, "No datasets found under data/actual or data/expected."

    # Pick the first dataset for testing
    dataset_name = sorted(datasets.keys())[0]
    ds_info = datasets[dataset_name]

    # -----------------------------
    # Resolve file paths
    # -----------------------------
    actual_files = sorted(ds_info["actual"])
    expected_files = sorted(ds_info["expected"])

    assert actual_files, f"No actual SQLite files for dataset '{dataset_name}'."
    assert expected_files, f"No expected CSV files for dataset '{dataset_name}'."

    actual_path = actual_files[0]
    expected_path = expected_files[0]

    # -----------------------------
    # Load datasets
    # -----------------------------
    loader = DataLoader(base_data_path=str(BASE_DATA_PATH))

    expected = loader.load(str(expected_path.relative_to(BASE_DATA_PATH)))

    table_name = TABLE_NAME_MAP.get(dataset_name, dataset_name)

    actual = loader.load_sqlite_table(
        str(actual_path.relative_to(BASE_DATA_PATH)),
        table_name,
    )

    # -----------------------------
    # Run validation
    # -----------------------------
    validator = Validator(key_field="id")
    result = validator.validate(expected, actual)

    # -----------------------------
    # Developer‑friendly summary
    # -----------------------------
    print_summary(f"Unified Dataset Validation: {dataset_name}", result)

    # -----------------------------
    # If FAIL → print differences
    # -----------------------------
    if result["status"] == "FAIL":
        print("\nDifferences found:")
        for diff in result.get("differences", []):
            print(f"- {diff}")

    # -----------------------------
    # Assert PASS/FAIL
    # -----------------------------
    assert result["status"] == "PASS"
