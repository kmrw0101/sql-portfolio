"""
conftest.py
-----------
Shared test utilities for the python_data_validator project.

Pytest automatically loads this file for all tests in this directory.
Anything defined here (like helper functions or fixtures) becomes
available to tests *without* needing an import.

Included:
- print_summary(): Pretty, unified summary output matching the CLI runner
  and Streamlit app formatting.
"""

def print_summary(test_name, result):
    """
    Print a clean, unified summary of a validation result.

    Parameters
    ----------
    test_name : str
        A descriptive label for the test being run.

    result : dict
        The dictionary returned by Validator.validate(), expected to contain:
            - "status": PASS or FAIL
            - "summary": dict of numeric counts
            - "differences": list of issue descriptions
    """

    print("\n" + "=" * 70)
    print(f"{test_name}")
    print("=" * 70)

    # Status
    status = result.get("status", "UNKNOWN")
    print(f"Status: {status}\n")

    # Summary counts
    summary = result.get("summary", {})
    print("Summary:")
    if summary:
        for key, value in summary.items():
            print(f"  {key}: {value}")
    else:
        print("  (none provided)")

    # Differences
    diffs = result.get("differences", [])
    print("\nDifferences:")
    if diffs:
        for diff in diffs:
            print(f"  - {diff}")
    else:
        print("  None")

    print("=" * 70 + "\n")
