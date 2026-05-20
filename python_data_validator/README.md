# Data Validation Framework

## Overview

This project is a Python-based data validation framework designed to compare actual datasets (SQLite) against expected datasets (CSV) and produce a clean, unified validation summary.

It supports:

- Auto-discovery of datasets
- Flexible table-name mapping
- A reusable validation engine
- A CLI runner for real-world use
- A pytest suite for automated testing
- Pretty, human-readable output summaries

A more user-friendly interface (GUI/Streamlit) is planned next.

---

## Project Structure

python_data_validator/
├── app/
│   ├── run_validator.py        # CLI entry point (python -m python_data_validator.app.run_validator)
│   └── validate_app.py         # Core app logic for running validations
│
├── framework/
│   ├── config.py               # Shared paths + dataset/table mapping
│   ├── data_loader.py          # Loads CSV + SQLite tables
│   ├── validators.py           # Validation engine
│   └── api_client.py           # (Reserved for future expansion)
│
├── data/
│   ├── actual/
│   │   ├── monsters.sqlite     # GOOD dataset
│   │   └── monsters_bad.sqlite # BAD dataset
│   │
│   └── expected/
│       └── monsters.csv        # Golden truth
│
├── tests/
│   ├── conftest.py             # Pretty summary helper for pytest
│   └── test_validator.py       # Automated validation test
│
└── README.md

---

## How the Framework Works

### DataLoader (framework/data_loader.py)

- Loads CSV files into pandas DataFrames
- Loads SQLite tables into DataFrames
- Normalizes column names
- Ensures consistent data types

### Validator (framework/validators.py)

- Compares expected vs actual
- Detects missing rows
- Detects extra rows
- Detects mismatched values
- Detects nulls
- Detects duplicate keys
- Returns a structured result dict:
  - status (PASS/FAIL)
  - summary (counts)
  - differences (list of issues)

### Config (framework/config.py)

- Defines base data paths
- Defines actual/ and expected/ directories
- Defines dataset → table name mapping
- Supports auto-discovery of datasets

---

## Running the Validator (Two Ways)

You can run this project in two completely different modes.

---

# 1. Run the Real Validator (CLI Mode)

This is the interactive version that real users run.

How to run it:

1. Open a terminal
2. Navigate to the project root (the folder that contains python_data_validator/):

       cd C:\git\KMR-portfolio

3. Run the CLI:

       python -m python_data_validator.app.run_validator

4. Follow the prompts to:
   - Select a dataset
   - Select an actual SQLite file
   - Select an expected CSV file
   - View validation results

This mode is interactive and will eventually be replaced by a GUI/Streamlit interface.

---

# 2. Run Automated Tests (Pytest Mode)

This is for developers and CI pipelines.

From the project root:

    pytest -vv -s

- -vv → verbose
- -s → show pretty printed summaries

Pytest uses the same DataLoader and Validator as the CLI, ensuring consistent behavior.

---

## Example Output

### Success Example (GOOD dataset)

======================================================================
Unified Dataset Validation: monsters
======================================================================
Status: PASS

Summary:
  missing_rows: 0
  extra_rows: 0
  mismatched_values: 0
  missing_columns: 0
  extra_columns: 0
  nulls: 0
  duplicates: 0

Differences:
  None
======================================================================

---

### Failure Example (BAD dataset)

This is the output when selecting monsters_bad.sqlite:

=== Data Validation CLI Runner ===

Select a dataset:
  1. monsters

Enter number: 1

Select actual SQLite file:
  1. monsters.sqlite
  2. monsters_bad.sqlite

Enter number: 2

Select expected CSV file:
  1. monsters.csv

Enter number: 1

Validating dataset 'monsters'...
  Actual:   monsters_bad.sqlite
  Expected: monsters.csv

=== Validation Results ===
Status: FAIL

Summary:
  missing_rows: 1
  extra_rows: 2
  mismatched_values: 1
  missing_columns: 0
  extra_columns: 0
  nulls: 1
  duplicates: 0

Differences:
  - {'type': 'missing_row', 'row': {'id': 3, 'name': 'Marsh Ghoul', 'type': 'undead', 'armor_class': 12, 'hit_points': 22, 'biome': 'swamp', 'challenge_rating': 2.0, 'size': 'medium', 'alignment': 'chaotic evil', 'notes': 'Ambush predator lurking in bogs'}}
  - {'type': 'extra_row', 'row': {'id': 7, 'name': 'Ember Lynx', 'type': 'elemental', 'armor_class': 15, 'hit_points': 42, 'biome': 'volcanic', 'challenge_rating': 2.0, 'size': 'medium', 'alignment': 'neutral', 'notes': 'Emits faint heat trails; hunts at dusk'}}
  - {'type': 'extra_row', 'row': {'id': 8, 'name': 'Mireback Tortoise', 'type': 'beast', 'armor_class': 17, 'hit_points': 85, 'biome': 'swamp', 'challenge_rating': 3.0, 'size': 'large', 'alignment': 'unaligned', 'notes': 'Slow but heavily armored; retracts when threatened'}}
  - {'type': 'mismatched_value', 'detail': {'key': 1, 'field': 'armor_class', 'expected': 14, 'actual': 'NULL'}}
  - {'type': 'null_value', 'detail': {'row_index': 0, 'field': 'armor_class', 'value': 'NULL'}}

---

## Future Enhancements

A more user-friendly interface is next on the roadmap:

- Interactive CLI improvements
- Streamlit Web App (upload CSV/SQLite, run validation, view diffs)
- GUI Dashboard (dataset browser, validation history, charts)

The backend is already modular and ready for these upgrades.

---

## Key Files

- app/run_validator.py — CLI entry point
- app/validate_app.py — main app logic
- framework/data_loader.py — CSV/SQLite loader
- framework/validators.py — validation engine
- tests/test_validator.py — pytest suite
