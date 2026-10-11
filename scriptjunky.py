#!/usr/bin/env python3
"""Run Script Junky without installing a package."""
import sys

if sys.version_info < (3, 11):
    raise SystemExit("Script Junky requires Python 3.11 or newer.")

from junky.cli import main

if __name__ == "__main__":
    main()
