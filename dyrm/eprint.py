#!/usr/bin/env python

"""
Screen-scraper for writers of fan fiction who want to keep
up to date on the hits their stories are getting.

This part is for reading and comparing the monthly story
totals.
"""

from __future__ import print_function
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    eprint("This is a test")


# Runs the script, checking for changes
if __name__ == "__main__":
    main()
