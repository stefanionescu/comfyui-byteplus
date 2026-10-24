"""Report the problems that a build script finds when it checks the shipped files."""

import sys


def report_problems(problems: list[str]) -> int:
    """Write each problem on its own line to standard error, and return 1 when there is any, else 0."""
    for problem in problems:
        sys.stderr.write(problem + '\n')
    return int(bool(problems))


__all__ = ['report_problems']
