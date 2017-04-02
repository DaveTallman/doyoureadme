#!/usr/bin/env python

"""
Page getter for Fanfiction.net and ao3
"""
import sys
import argparse
import logging
from dyrm import ffmonthly, do_you_read_ao3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--nomonth",
        help="no monthly",
        action="store_true")
    parser.add_argument(
        "-a", "--ao3",
        help="look at ao3",
        action="store_true")
    parser.add_argument(
        "-o", "--out",
        help="echo to stdout",
        action="store_true")
    parser.add_argument(
        "-c", "--catchup",
        help="catch up totals",
        action="store_true")
    parser.add_argument(
        "-d", "--database",
        type=str,
        default="dbs/readme.db",
        help="path to sqlite3 database")
    parser.add_argument(
        "-l", "--logfile",
        type=str,
        default="logs/ooo.txt",
        help="path to log file")
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.logfile,
        format='%(message)s',
        level=logging.INFO)
    if args.out:
        root = logging.getLogger()
        hand = logging.StreamHandler(sys.stdout)
        root.addHandler(hand)

    logging.info("fanfiction.net")

    ffmonthly.main(args.database, catchup=args.catchup, nomonth=args.nomonth)
    if args.ao3:
        logging.info("ao3")
        do_you_read_ao3.main(args.database)


# Drive the main routine
if __name__ == "__main__":
    main()
