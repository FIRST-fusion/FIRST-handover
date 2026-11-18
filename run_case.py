#!/usr/bin/env python3
"""FIRST 單一入口：python3 run_case.py INPUT_FILE_OR_DIRECTORY。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools'))
from run_case import main

if __name__ == '__main__':
    sys.exit(main())
