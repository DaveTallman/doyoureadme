#!/usr/bin/env python

"""
Page getter for Fanfiction.net and ao3
"""
import sys
import argparse
import logging
from dyrm.eprint import eprint
from dyrm.ffgetter import PageGetter, FanfictionGetter, FanfictionScraper
from dyrm.readme_db import ReadMeDb, Comments, SComments, Aliases


def do_comment_page(getter, scraper, read_db, sref):
    """ Comment extraction to db """

    link = "r/" + str(sref) + "/"
    comment_tree = getter.get_comment_tree(link)

    dates = []
    chapters = []
    text_comments = []
    signers = []
    while True:
        mynext, dates1, chapters1, text_comments1, signers1 =\
            scraper.get_comments(comment_tree)
        dates = dates + dates1
        chapters = chapters + chapters1
        text_comments = text_comments + text_comments1
        signers = signers + signers1
        if mynext:
            comment_tree = getter.get_comment_tree(mynext)
        else:
            break

    print(len(dates), " total comments")
    clist = [x for x in zip(dates, chapters, text_comments, signers)]
    for date, chap, text, sign in reversed(clist):
        print(date, chap, text, sign)
        new_rec = Comments(
            stamp=date, ref=sref, chapter=chap, name=sign[1], comment=text)
        if sign[0] != 0:
            user = read_db.get_or_create_user(sign[0], "Unknown")
            if not user.aliases:
                user.aliases = [Aliases(name=sign[1])]
            new_rec.signed = [SComments(code=sign[0])]
        read_db.session.add(new_rec)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--story",
        type=str,
        help="story",
        default="10913419")
    parser.add_argument(
        "-o", "--out",
        help="echo to stdout",
        action="store_true")
    parser.add_argument(
        "-l", "--logfile",
        type=str,
        default="ccc.txt",
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

    logging.info("fanfiction.net comments for " + args.story)

    scraper = FanfictionScraper()

    with ReadMeDb(echo=False) as read_db:
        try:
            with PageGetter() as pgetter:
                getter = FanfictionGetter(pgetter)

                stories = read_db.get_stories()
                for story in sorted(stories, key=lambda x: x.title):
                    print(story.title)
                    do_comment_page(
                        getter, scraper, read_db, story.ref)

                pgetter.stop_sleep()

        except ConnectionRefusedError:
            eprint("Need to be logged in to fanfiction.net")
        except ConnectionAbortedError as exc:
            eprint("Connection problem", exc)

        read_db.set_commit_flag()


# Drive the main routine
if __name__ == "__main__":
    main()
