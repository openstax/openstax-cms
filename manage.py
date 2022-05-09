#!/usr/bin/python3
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openstax.settings")

    # run coverage.py around tests automatically
    try:
        command = sys.argv[1]
    except IndexError:
        command = "help"

    running_tests = command == "test"
    if running_tests:
        from coverage import Coverage

        cov = Coverage()
        cov.erase()
        cov.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    if running_tests:
        cov.stop()
        cov.save()
        covered = cov.report()


if __name__ == "__main__":
    main()
