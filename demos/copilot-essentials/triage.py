#!/usr/bin/env python3
"""
Quick log triage utility
────────────────────────
  • Accepts   *.log  or  *.log.gz
  • Filters   last N minutes (sliding window)
  • Tallies   (status‑code, endpoint) pairs
  • Optional  --status 499,321 for focused searching

  A noisy incident page reveals a spike in 321 or 499 errors, but the observability stack is lagging. You need a quick, local log sweep to spot patterns and counts.
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import gzip
import re
import sys
from collections import Counter
from typing import Iterable, Tuple


def read_lines(file_path: Path) -> Iterable[str]:
    """Open plain or gzipped log file and yield each line (stripped)."""
    if file_path.suffix == ".gz":
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                yield line.strip()
    


LOG_PATTERN = re.compile(
    r'^\S+ \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?:\S+) (?P<path>\S+) [^"]+" (?P<status>\d{3})\b'
)


def parse_line(line: str) -> Tuple[datetime, int, str] | None:
    """Return (timestamp_utc, status_code_int, url_path) or None if malformed."""
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    timestamp_str = match.group("timestamp")
    path = match.group("path")
    status_str = match.group("status")

    try:
        timestamp = datetime.strptime(timestamp_str, "%d/%b/%Y:%H:%M:%S %z")
        timestamp_utc = timestamp.astimezone(timezone.utc)
        status_code = int(status_str)
        return timestamp_utc, status_code, path
    except ValueError:
        return None




def triage(
    lines: Iterable[str],
    minutes: int,
    wanted_status: set[int] | None
) -> Counter[Tuple[int, str]]:
    """Aggregate counts for lines within the window and matching status filter."""
    now_utc = datetime.now(timezone.utc)
    window_start = now_utc - timedelta(minutes=max(minutes, 0))
    counter: Counter[Tuple[int, str]] = Counter()

    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            continue

        timestamp_utc, status_code, path = parsed
        if timestamp_utc < window_start or timestamp_utc > now_utc:
            continue
        if wanted_status is not None and status_code not in wanted_status:
            continue

        counter[(status_code, path)] += 1

    return counter




def render(counter: Counter[Tuple[int, str]], top: int) -> None:
    """Pretty‑print a Markdown‑style table of the top offenders."""
    print("| Rank | Status | Path | Hits |")
    print("|------|--------|------|------|")
    for rank, ((status_code, path), hits) in enumerate(counter.most_common(top), start=1):
        print(f"| {rank} | {status_code} | {path} | {hits} |")


def main() -> None:
    """Wire everything together with argparse CLI options."""
    parser = argparse.ArgumentParser(description="Quick log triage utility")
    parser.add_argument("file", type=Path, help="Path to the log file (.log or .log.gz)")
    parser.add_argument("--minutes", type=int, default=15, help="Time window in minutes (default: 15)")
    parser.add_argument("--status", type=str, help="Comma-separated list of status codes to filter (optional)")
    parser.add_argument("--top", type=int, default=10, help="Number of top results to display (default: 10)")

    args = parser.parse_args()

    if args.minutes < 0:
        parser.error("--minutes must be zero or greater")
    if args.top < 1:
        parser.error("--top must be one or greater")

    wanted_status = None
    if args.status:
        try:
            wanted_status = {int(code.strip()) for code in args.status.split(",") if code.strip()}
        except ValueError:
            parser.error("--status must be a comma-separated list of integers")

    if wanted_status is not None and not wanted_status:
        parser.error("--status must contain at least one integer")

    try:
        lines = read_lines(args.file)
        counter = triage(lines, args.minutes, wanted_status)
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        print(f"Error reading {args.file}: {error}", file=sys.stderr)
        raise SystemExit(1)

    if not counter:
        print("No matches found.", file=sys.stderr)
        raise SystemExit(1)

    render(counter, args.top)


if __name__ == "__main__":
    main()
