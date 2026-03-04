#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import shutil
import sys
from pathlib import Path


def _ensure_postgres_cli_on_path() -> None:
    if os.name != 'nt' or shutil.which('psql'):
        return

    postgres_root = Path(r"C:\Program Files\PostgreSQL")
    if not postgres_root.exists():
        return

    candidate_bins = sorted(
        (
            child / 'bin'
            for child in postgres_root.iterdir()
            if child.is_dir() and (child / 'bin' / 'psql.exe').exists()
        ),
        reverse=True,
    )

    if candidate_bins:
        os.environ['PATH'] = f"{candidate_bins[0]}{os.pathsep}{os.environ.get('PATH', '')}"


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    _ensure_postgres_cli_on_path()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
