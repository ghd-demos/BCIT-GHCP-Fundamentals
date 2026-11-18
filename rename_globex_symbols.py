#!/usr/bin/env python3
"""Recursively rename legacy-prefixed files and symbols."""

from __future__ import annotations

import argparse
import logging
import os
import re
from pathlib import Path

LEGACY_PREFIX = "glob" + "ex_"
NEW_PREFIX = "chrom" + "a_"
EXCLUDED_DIRECTORIES = frozenset({".git", "node_modules"})
BINARY_FILE = -1
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
SYMBOL_PATTERN = re.compile(
	rf"(?<![A-Za-z0-9_]){re.escape(LEGACY_PREFIX)}[A-Za-z0-9_]*"
)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def iter_files(root: Path):

	"""Yield files while pruning excluded directories."""
	for current_root, directory_names, file_names in os.walk(root):
		directory_names[:] = [
			name for name in directory_names if name not in EXCLUDED_DIRECTORIES
		]
		for file_name in file_names:
			path = Path(current_root, file_name)
			if not path.is_symlink():
				yield path


def update_symbols(path: Path, check: bool) -> int:
	"""Replace legacy-prefixed symbols in a UTF-8 file."""
	raw_content = path.read_bytes()
	try:
		content = raw_content.decode("utf-8")
	except UnicodeDecodeError:
		return BINARY_FILE

	updated, count = SYMBOL_PATTERN.subn(
		lambda match: NEW_PREFIX + match.group(0)[len(LEGACY_PREFIX) :],
		content,
	)
	if count and not check:
		path.write_bytes(updated.encode("utf-8"))
	return count


def new_file_path(path: Path) -> Path:
	"""Calculate a renamed path when the basename has the legacy prefix."""
	if not path.name.startswith(LEGACY_PREFIX):
		return path
	return path.with_name(NEW_PREFIX + path.name[len(LEGACY_PREFIX) :])


def run(root: Path, check: bool) -> int:
	"""Rename matching content and files, returning a process exit code."""
	files = list(iter_files(root))
	content_changes = 0
	replacements = 0
	renames = 0
	binary_skipped = 0
	errors = 0

	for path in files:
		try:
			count = update_symbols(path, check)
		except OSError as error:
			LOGGER.error("Cannot process %s: %s", path, error)
			errors += 1
			continue

		if count == BINARY_FILE:
			LOGGER.debug("Skipped binary file: %s", path)
			binary_skipped += 1
			continue

		if count:
			content_changes += 1
			replacements += count

		destination = new_file_path(path)
		if destination == path:
			continue
		if destination.exists():
			LOGGER.error("Cannot rename %s: %s exists", path, destination)
			errors += 1
			continue

		LOGGER.info("%s: %s -> %s", "Would rename" if check else "Renaming", path, destination)
		if not check:
			try:
				path.rename(destination)
			except OSError as error:
				LOGGER.error("Cannot rename %s: %s", path, error)
				errors += 1
				continue
		renames += 1

	LOGGER.info("Summary")
	LOGGER.info("Files scanned: %d", len(files))
	LOGGER.info("Files with symbol changes: %d", content_changes)
	LOGGER.info("Symbol replacements: %d", replacements)
	LOGGER.info("Files renamed: %d", renames)
	LOGGER.info("Binary files skipped: %d", binary_skipped)
	LOGGER.info("Errors: %d", errors)
	LOGGER.info("Check mode: %s", "yes" if check else "no")

	if errors or (check and (replacements or renames)):
		return EXIT_FAILURE
	return EXIT_SUCCESS


def main() -> int:

	"""Parse command-line options and execute the rename."""
	logging.basicConfig(level=logging.INFO, format="%(message)s")
	parser = argparse.ArgumentParser(
		description="Recursively rename legacy-prefixed files and symbols."
	)

	parser.add_argument(
		"root",
		nargs="?",
		type=Path,
		default=Path.cwd(),
		help="Directory to process (default: current directory)",
	)
	parser.add_argument(
		"--check",
		action="store_true",
		help="Report required changes without modifying files and fail if found",
	)
	args = parser.parse_args()

	root = args.root.resolve()
	if not root.is_dir():
		parser.error(f"Not a directory: {root}")
	return run(root, args.check)


if __name__ == "__main__":
	raise SystemExit(main())
