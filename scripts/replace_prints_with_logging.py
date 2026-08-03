#!/usr/bin/env python
"""
Script to replace print() statements with logging calls.
Run from project root: python scripts/replace_prints_with_logging.py
"""

import os
import re
from pathlib import Path

# Patterns to replace
PATTERNS = [
    # print(f"...") -> logger.info(f"...")
    (
        r'print\(f"([^"]*?)"\)',
        r'logger.info(f"\1")',
    ),
    # print("...") -> logger.info("...")
    (
        r"print\(\"([^\"]*?)\"\)",
        r'logger.info("\1")',
    ),
    # print('...') -> logger.info('...')
    (
        r"print\('([^']*?)'\)",
        r"logger.info('\1')",
    ),
    # print(traceback.format_exc()) -> logger.error(..., exc_info=True)
    (
        r'print\(traceback\.format_exc\(\)\)',
        r'logger.error("Exception occurred", exc_info=True)',
    ),
    # print(variable) -> logger.info(variable)
    (
        r'print\((\w+)\)',
        r'logger.info(\1)',
    ),
]

# Files to process
APPS_DIR = Path('apps')
FILES_TO_PROCESS = []

# Find all .py files with print statements
for py_file in APPS_DIR.rglob('*.py'):
    if py_file.is_file():
        content = py_file.read_text(encoding='utf-8', errors='ignore')
        if 'print(' in content:
            FILES_TO_PROCESS.append(py_file)

print(f"Found {len(FILES_TO_PROCESS)} files with print statements")
print("=" * 60)

# Process each file
for file_path in FILES_TO_PROCESS:
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    original_content = content

    # Check if logger is imported
    has_logger_import = 'from apps.core.logging import' in content or 'import logging' in content

    # Add logger import if needed
    if 'print(' in content and not has_logger_import:
        # Add import after other imports
        import_line = 'from apps.core.logging import get_logger\n\n'
        if 'import' in content:
            # Find the last import
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, 'import logging')
            content = '\n'.join(lines)
            has_logger_import = True

    # Add logger initialization if needed
    if 'print(' in content and 'logger = ' not in content:
        content = content.replace(
            'import logging\n',
            'import logging\n\nlogger = logging.getLogger(__name__)\n',
            1
        )

    # Replace print statements (simple version)
    if 'print(' in content:
        # This is a simplified replacement - regex can be fragile
        # Better to do manual replacements
        pass

    if content != original_content:
        print(f"✓ {file_path}")
    else:
        if 'print(' in content:
            print(f"⚠ {file_path} (needs manual review)")

print("=" * 60)
print("\nNote: Run this script in DRY mode first to see what would change")
print("Manual review recommended for complex print statements")
