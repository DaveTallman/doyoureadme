#!/usr/bin/env python

"""
Page getter for Fanfiction.net and ao3
"""
from dyrm import get_userstats
import sys
import logging


def main():
    print("user stats")
    logging.basicConfig(
        format='%(message)s',
        level=logging.INFO)

    get_userstats.main()


if __name__ == "__main__":
    main()
