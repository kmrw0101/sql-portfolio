"""
App: Data Validation Tool (Streamlit)
Provides a user-friendly interface for validating SQLite datasets against
expected CSV files. Automatically discovers datasets, loads actual and expected
data, compares them, and displays differences visually. This version includes
expanded notes to support learning and clarity.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from python_data_validator.framework.data_loader import DataLoader
from python_data_validator.framework.validators import Validator
from python_data_validator.framework.config import BASE_DATA_PATH, TABLE_NAME_MAP
import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Configuration and Paths
# ---------------------------------------------------------------------------
# These paths define where the app looks for actual SQLite files and expected
# CSV files. The folder structure is intentionally simple so the tool can be
# expanded to support any dataset without modifying the code.
#
# Expected structure:
#   mini-project/data/actual/*.sqlite
#   mini-project/data/expected/*.csv
#
# The app will scan these folders and automatically group files into datasets.
# ---------------------------------------------------------------------------

PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
ACTUAL_DIR: Path = PROJECT_ROOT / "mini-project" / "data" / "actual"
EXPECTED_DIR: Path = PROJECT_ROOT / "mini-project" / "data" / "expected"


# ---------------------------------------------------------------------------
# Dataset Discovery
# ---------------------------------------------------------------------------
# Dataset discovery is responsible for:
#   - scanning the actual/ and expected/ folders
#   - identifying all SQLite and CSV files
#   - grouping them by dataset name
#
# A dataset name is inferred from the filename before the first underscore.
# Example:
#   monsters.sqlite          → dataset "monsters"
#   monsters_bad.sqlite      → dataset "monsters"
#   employees_2024.sqlite    → dataset "employees"
#
# This makes the tool expandable without code changes.
# ---------------------------------------------------------------------------

def infer_dataset_name(path: Path) -> str:
    """
    Extracts the dataset name from a file path by taking everything before the
    first underscore. If no underscore exists, the entire stem is used.
    """
    stem = path.stem
    if "_" in stem:
        return stem.split("_", 1)[0]
    return stem


def discover_datasets() -> Dict[str, Dict[str, List[Path]]]:
    """
    Scans the actual/ and expected/ directories and groups files into datasets.

    Returns a structure like:
    {
        "monsters": {
            "actual": [Path("monsters.sqlite"), Path("monsters_bad.sqlite")],
            "expected": [Path("monsters.csv")]
        },
        "employees": {
            "actual": [Path("employees.sqlite")],
            "expected": [Path("employees.csv")]
        }
    }
    """
    datasets: Dict[str, Dict[str, List[Path]]] = {}

    # Scan for SQLite files (actual data)
    for db_path in ACTUAL_DIR.glob("*.sqlite"):
        ds = infer_dataset_name(db_path)
        datasets.setdefault(ds, {"actual": [], "expected": []})
        datasets[ds]["actual"].append(db_path)

    # Scan for CSV files (expected data)
    for csv_path in EXPECTED_DIR.glob("*.csv"):
        ds = infer_dataset_name(csv_path)
        datasets.setdefault(ds, {"actual": [], "expected": []})
        datasets[ds]["expected"].append(csv_path)

    return datasets


# ---------------------------------------------------------------------------
# Data Loading Functions
# ---------------------------------------------------------------------------
# These functions load the actual SQLite data and expected CSV data into
# pandas DataFrames. They are intentionally simple and testable.
# ---------------------------------------------------------------------------

def load_sqlite_table(db_path: Path, table_name: str) -> pd.DataFrame:
    """
    Loads a table from a SQLite database into a DataFrame.
    """
    conn = sqlite3.connect(db_path)
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df


def load_csv(csv_path: Path) -> pd.DataFrame:
    """
    Loads a CSV file into a DataFrame.
    """
    return pd.read_csv(csv_path)


# ---------------------------------------------------------------------------
# Comparison Engine
# ---------------------------------------------------------------------------
# This is the core validation logic. It compares:
#   - missing rows (in expected but not actual)
#   - unexpected rows (in actual but not expected)
#   - mismatched values (same row, different values)
#
# The Streamlit UI simply displays the results returned by this function.
# ---------------------------------------------------------------------------

def align_and_compare(
    actual: pd.DataFrame,
    expected: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compares actual vs expected data and returns:
        missing_rows     → rows in expected but not in actual
        unexpected_rows  → rows in actual but not in expected
        diffs_df         → rows where values differ
    """
    actual = actual.copy()
    expected = expected.copy()

    # Sort by ID if present for consistent comparison
    if "id" in actual.columns and "id" in expected.columns:
        actual = actual.sort_values("id").reset_index(drop=True)
        expected = expected.sort_values("id").reset_index(drop=True)

    # Only compare columns that exist in both datasets
    common_cols = [c for c in expected.columns if c in actual.columns]
    actual_common = actual[common_cols]
    expected_common = expected[common_cols]

    # Use ID as the key if available
    key_cols = ["id"] if "id" in common_cols else common_cols

    # Merge to detect missing/unexpected rows
    merged = expected_common.merge(
        actual_common,
        on=key_cols,
        how="outer",
        indicator=True,
        suffixes=("_expected", "_actual"),
    )

    missing_rows = merged.loc[merged["_merge"] == "left_only", key_cols]
    unexpected_rows = merged.loc[merged["_merge"] == "right_only", key_cols]

    # Identify mismatched values
    diffs = []
    common_rows = merged.loc[merged["_merge"] == "both"].reset_index(drop=True)

    for col in common_cols:
        if col in key_cols:
            continue

        exp_col = f"{col}_expected"
        act_col = f"{col}_actual"

        mismatch_mask = common_rows[exp_col] != common_rows[act_col]
        mismatches = common_rows.loc[mismatch_mask, key_cols + [exp_col, act_col]]

        for _, row in mismatches.iterrows():
            diff_record = {"column": col}
            for k in key_cols:
                diff_record[k] = row[k]
            diff_record["expected"] = row[exp_col]
            diff_record["actual"] = row[act_col]
            diffs.append(diff_record)

    diffs_df = pd.DataFrame(diffs) if diffs else pd.DataFrame(
        columns=(key_cols + ["column", "expected", "actual"])
    )

    return missing_rows, unexpected_rows, diffs_df


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
# This section defines the user interface:
#   - dataset dropdown
#   - file selectors
#   - table name input
#   - run button
#   - results display (tables + charts)
#
# The UI does not contain business logic. It simply orchestrates user input
# and displays the output of the comparison engine.
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Data Validation Tool",
        layout="wide",
    )

    st.title("🧪 Data Validation Tool")
    st.write("Validate SQLite datasets against expected CSV files.")

    # Discover datasets dynamically
    datasets = discover_datasets()
    if not datasets:
        st.error("No datasets found. Add files under data/actual and data/expected.")
        return

    # Dataset dropdown
    dataset_names = sorted(datasets.keys())
    selected_dataset = st.selectbox("Select dataset", dataset_names)

    ds_info = datasets[selected_dataset]
    actual_files = ds_info["actual"]
    expected_files = ds_info["expected"]

    if not actual_files:
        st.error(f"No SQLite files found for dataset `{selected_dataset}`.")
        return
    if not expected_files:
        st.error(f"No CSV files found for dataset `{selected_dataset}`.")
        return

    # File selectors
    actual_display = {p.name: p for p in sorted(actual_files)}
    expected_display = {p.name: p for p in sorted(expected_files)}

    col1, col2 = st.columns(2)
    with col1:
        actual_choice = st.selectbox("Select actual SQLite file", list(actual_display.keys()))
    with col2:
        expected_choice = st.selectbox("Select expected CSV file", list(expected_display.keys()))

    # Table name input (defaults to dataset name)
    table_name = st.text_input(
        "Table name in SQLite",
        value=selected_dataset,
        help="Defaults to the dataset name; change if needed.",
    )

    # Run button
    run = st.button("Run Validation", type="primary")
    if not run:
        return

    actual_path = actual_display[actual_choice]
    expected_path = expected_display[expected_choice]

    st.info(f"Validating `{selected_dataset}` using `{actual_path.name}` vs `{expected_path.name}`.")

    # Load data
    try:
        actual_df = load_sqlite_table(actual_path, table_name)
    except Exception as exc:
        st.error(f"Failed to load table `{table_name}` from `{actual_path.name}`.\n\n{exc}")
        return

    try:
        expected_df = load_csv(expected_path)
    except Exception as exc:
        st.error(f"Failed to load expected CSV `{expected_path.name}`.\n\n{exc}")
        return

    # Compare
    missing_rows, unexpected_rows, diffs_df = align_and_compare(actual_df, expected_df)

    # Results summary
    if missing_rows.empty and unexpected_rows.empty and diffs_df.empty:
        st.success("✅ Validation passed. No differences found.")
    else:
        st.error("❌ Differences detected.")

    # Summary panel
    with st.expander("Summary", expanded=True):
        st.write(f"Rows in actual: **{len(actual_df)}**")
        st.write(f"Rows in expected: **{len(expected_df)}**")
        st.write(f"Missing rows: **{len(missing_rows)}**")
        st.write(f"Unexpected rows: **{len(unexpected_rows)}**")
        st.write(f"Mismatched cells: **{len(diffs_df)}**")

    # Detailed panels
    if not missing_rows.empty:
        st.subheader("Missing rows")
        st.dataframe(missing_rows)

    if not unexpected_rows.empty:
        st.subheader("Unexpected rows")
        st.dataframe(unexpected_rows)

    if not diffs_df.empty:
        st.subheader("Value mismatches")
        st.dataframe(diffs_df)

        # Optional chart
        if "column" in diffs_df.columns:
            chart_data = (
                diffs_df["column"]
                .value_counts()
                .rename_axis("column")
                .reset_index(name="mismatch_count")
            )
            st.subheader("Mismatches by column")
            st.bar_chart(chart_data.set_index("column"))


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
