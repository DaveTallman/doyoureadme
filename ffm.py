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
        "-d", "--database",
        type=str,
        default="dbs/readme.db",
        help="path to sqlite3 database")
    parser.add_argument(
        "-l", "--logfile",
        type=str,
        default="logs/ooo.txt",
        help="path to log file")
    parser.add_argument(
        "-t", "--timedelay",
        type=float,
        default=8.0,
        help="time delay between page gets in seconds")
    parser.add_argument(
        "-m", "--maxtime",
        type=float,
        default=18.0,
        help="max time to wait for page")
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.logfile,
        format='%(message)s',
        level=logging.INFO)
    if args.out:
        hand = logging.StreamHandler(sys.stdout)
        hand.setLevel(logging.INFO)
        form = logging.Formatter('%(message)s')
        hand.setFormatter(form)
        logging.getLogger('').addHandler(hand)

    logger = logging.getLogger(__name__)
    logger.info("fanfiction.net")

    ffmonthly.main(
        args.database, nomonth=args.nomonth,
        delay=args.timedelay, timeout=args.maxtime)
    if args.ao3:
        logger.info("ao3")
        do_you_read_ao3.main(args.database)


# Drive the main routine
if __name__ == "__main__":
    main()
