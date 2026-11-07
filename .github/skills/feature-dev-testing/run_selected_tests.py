"""Run selected test suites through `main.py --test` and print a short report.

Other suite registrations in tests/init_tests.py are commented out for the run and always restored afterwards.

Usage (from the repository root):
    .venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py TestInvestments TestReminders
    .venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py          # full suite
    .venv1/bin/python .github/skills/feature-dev-testing/run_selected_tests.py --list
"""

from __future__ import annotations
import argparse
import re
import subprocess
import sys
from pathlib import Path



ROOT = Path(__file__).resolve().parents[3]
INIT_TESTS = ROOT / "tests" / "init_tests.py"
OUTPUT_FILE = Path("/tmp/account_organizer_tests.txt")
SUITE_LINE = re.compile(r"^(\s*)(loader\.loadTestsFromTestCase\((\w+)\),)$", re.MULTILINE)
RESULT_LINE = re.compile(r"^(FAIL|ERROR): ")
SUMMARY_PREFIXES = ("Tests found", "Ran ", "OK", "FAILED")


def select_suites(source:str, suites:list[str]) -> str:
    """Comment out registrations of suites that aren't selected.

        Arguments
        ---------
            `source` : (str) - Content of tests/init_tests.py.
            `suites` : (list[str]) - Names of suites to keep.
        Returns
        -------
            `str` - Modified content.
    """

    unknown = set(suites) - {match[2] for match in SUITE_LINE.findall(source)}
    if unknown:
        sys.exit(f"Unknown suites: {', '.join(sorted(unknown))}. Use --list to see available suites.")

    return SUITE_LINE.sub(
        lambda match: match.group(0) if match.group(3) in suites else f"{match.group(1)}# {match.group(2)}",
        source
    )


def print_report(output:str) -> None:
    """Print summary lines and details of failed tests.

        Arguments
        ---------
            `output` : (str) - Output of the test run.
    """

    lines = output.splitlines()
    for line in lines:
        if line.startswith(SUMMARY_PREFIXES):
            print(line)

    # Detailed failure blocks start after a "=====" line and end before the next one
    for index, line in enumerate(lines):
        if RESULT_LINE.match(line) and index > 0 and lines[index - 1].startswith("====="):
            print("\n" + line)
            for detail in lines[index + 1:]:
                if detail.startswith("====="):
                    break
                print(detail)


def main() -> None:
    """Run the selected suites and exit with code 1 if any test failed."""

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("suites", nargs="*", help="Test case class names to run. Runs all suites if empty.")
    parser.add_argument("--list", action="store_true", help="List registered suites and exit")
    args = parser.parse_args()

    original_source = INIT_TESTS.read_text(encoding="utf-8")
    if args.list:
        print("\n".join(match[2] for match in SUITE_LINE.findall(original_source)))
        return

    try:
        if args.suites:
            INIT_TESTS.write_text(select_suites(original_source, args.suites), encoding="utf-8")
        with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
            subprocess.run(
                [sys.executable, "main.py", "--test"], cwd=ROOT, stdout=output_file, stderr=subprocess.STDOUT
            )
    finally:
        INIT_TESTS.write_text(original_source, encoding="utf-8")

    output = OUTPUT_FILE.read_text(encoding="utf-8", errors="replace")
    print_report(output)
    print(f"\nFull output: {OUTPUT_FILE}")
    sys.exit(0 if "\nOK" in output and "Ran " in output else 1)


if __name__ == "__main__":
    main()
