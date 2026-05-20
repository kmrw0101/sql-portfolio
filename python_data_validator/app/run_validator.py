"""
App: Data Validation CLI Runner

This script provides a command‑line interface for validating SQLite datasets
against expected CSV files. It mirrors the architecture of the Streamlit app
so the backend stays consistent, predictable, and GUI‑ready.

This runner handles:
- Dataset auto‑discovery
- User selection of dataset + files
- Loading actual and expected data
- Running validation
- Pretty printing results

Sections:
- Imports
- Configuration (from shared config.py)
- Dataset discovery
- User selection helpers
- Main runner
- Entry point
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from pathlib import Path
from typing import Dict, List

from python_data_validator.framework.data_loader import DataLoader
from python_data_validator.framework.validators import Validator
from python_data_validator.framework.config import BASE_DATA_PATH, TABLE_NAME_MAP


# Import shared configuration (scalable Option 2)
from python_data_validator.framework.config import (
    BASE_DATA_PATH,
    ACTUAL_DIR,
    EXPECTED_DIR,
    TABLE_NAME_MAP,
)


# ---------------------------------------------------------------------------
# Dataset Discovery
# ---------------------------------------------------------------------------
# These functions mirror the Streamlit app and allow both tools to:
#   - scan actual/ for *.sqlite
#   - scan expected/ for *.csv
#   - infer dataset names from filenames
#   - group files by dataset
#
# The underscore rule:
#   monsters.sqlite        → "monsters"
#   monsters_bad.sqlite    → "monsters"
# ---------------------------------------------------------------------------

def infer_dataset_name(path: Path) -> str:
    stem = path.stem
    return stem.split("_", 1)[0] if "_" in stem else stem


def discover_datasets() -> Dict[str, Dict[str, List[Path]]]:
    datasets: Dict[str, Dict[str, List[Path]]] = {}

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
# User Selection Helpers
# ---------------------------------------------------------------------------
# These helpers provide a simple CLI interface for choosing:
#   - dataset
#   - actual SQLite file
#   - expected CSV file
#
# This keeps the runner interactive but still GUI‑ready.
# A future GUI will replace these with dropdowns or file pickers.
# ---------------------------------------------------------------------------

def choose_from_list(prompt: str, items: List[str]) -> str:
    print(f"\n{prompt}")
    for i, item in enumerate(items, start=1):
        print(f"  {i}. {item}")
    choice = int(input("\nEnter number: "))
    return items[choice - 1]


# ---------------------------------------------------------------------------
# Main Runner
# ---------------------------------------------------------------------------
# This is the orchestrator:
#   - discovers datasets
#   - prompts user for selections
#   - loads actual + expected data
#   - applies TABLE_NAME_MAP
#   - runs validation
#   - prints results
#
# A GUI will eventually call the same logic, but without input() or print().
# ---------------------------------------------------------------------------

def main() -> None:
    print("\n=== Data Validation CLI Runner ===")

    # Discover datasets
    datasets = discover_datasets()
    if not datasets:
        print("No datasets found under data/actual or data/expected.")
        return

    # Dataset selection
    dataset_names = sorted(datasets.keys())
    selected_dataset = choose_from_list("Select a dataset:", dataset_names)
    ds_info = datasets[selected_dataset]

    # File selection
    actual_files = sorted(ds_info["actual"])
    expected_files = sorted(ds_info["expected"])

    if not actual_files:
        print(f"No actual SQLite files found for dataset '{selected_dataset}'.")
        return
    if not expected_files:
        print(f"No expected CSV files found for dataset '{selected_dataset}'.")
        return

    actual_choice = choose_from_list(
        "Select actual SQLite file:",
        [p.name for p in actual_files],
    )
    expected_choice = choose_from_list(
        "Select expected CSV file:",
        [p.name for p in expected_files],
    )

    actual_path = next(p for p in actual_files if p.name == actual_choice)
    expected_path = next(p for p in expected_files if p.name == expected_choice)

    print(f"\nValidating dataset '{selected_dataset}'...")
    print(f"  Actual:   {actual_path.name}")
    print(f"  Expected: {expected_path.name}")

    # Determine table name using TABLE_NAME_MAP
    table_name = TABLE_NAME_MAP.get(selected_dataset, selected_dataset)

    # Load data
    loader = DataLoader(base_data_path=str(BASE_DATA_PATH))
    expected = loader.load(str(expected_path.relative_to(BASE_DATA_PATH)))
    actual = loader.load_sqlite_table(
        str(actual_path.relative_to(BASE_DATA_PATH)),
        table_name,
    )

    # Run validation
    validator = Validator(key_field="id")
    result = validator.validate(expected, actual)

    # Pretty print results
    print("\n=== Validation Results ===")
    print(f"Status: {result['status']}\n")

    print("Summary:")
    for k, v in result["summary"].items():
        print(f"  {k}: {v}")

    print("\nDifferences:")
    if not result["differences"]:
        print("  None")
    else:
        for diff in result["differences"]:
            print(f"  - {diff}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
# This block makes the file a CLI runner.
# When executed directly (python -m app.run_validator), main() runs.
# When imported by a GUI or test suite, main() does NOT run.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
