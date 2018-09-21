#!/usr/bin/env python

"""
Screen-scraper for writers of fan fiction who want to keep
up to date on the hits their stories are getting,
specialized in this case for an archive of our own (ao3)
"""

import sys
import logging
from lxml import etree
import dyrm.read_firefox_cookies as read_firefox_cookies
from dyrm.eprint import eprint
from dyrm.ffgetter import PageGetter
from dyrm.readme_db import ReadMeDb
from dyrm.reportgen import ReportGen


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class Ao3Scraper:
    """ Encapsulates the scraping of data from ao3 """

    def __init__(self):
        self.find_stats = etree.XPath('//dl[@class = "stats"]')
        self.find_hits = etree.XPath('dd[@class = "hits"]')
        self.find_kudos = etree.XPath('dd[@class = "kudos"]')
        self.find_comments = etree.XPath('dd[@class = "comments"]')
        self.find_bookmarks = etree.XPath('dd[@class = "bookmarks"]')
        self.find_headers = etree.XPath(
            '//div[@class ="header module"]/h4[@class = "heading"]/a[contains(@href,"works")]')

    def parse_tree(self, tree, recs):
        stats = self.find_stats(tree)
        headers = self.find_headers(tree)

        for header, stat_block in zip(headers, stats):
            title = header.text_content()
            ref = int(header.get("href")[7:])
            hit_list = self.find_hits(stat_block)
            if hit_list:
                hits = int(hit_list[0].text_content())
            else:
                hits = 0
            kudo_list = self.find_kudos(stat_block)
            if kudo_list:
                kudos = int(kudo_list[0].text_content())
            else:
                kudos = 0
            comment_list = self.find_comments(stat_block)
            if comment_list:
                comments = int(comment_list[0].text_content())
            else:
                comments = 0
            bookmark_list = self.find_bookmarks(stat_block)
            if bookmark_list:
                bookmarks = int(bookmark_list[0].text_content())
            else:
                bookmarks = 0
            recs.append({
                "title": title,
                "ref": ref,
                "hits": hits, "kudos": kudos,
                "comments": comments, "bookmarks": bookmarks})
        return recs


def compare_ao3_rec(db_rec, current_rec, report_gen):
    """
    Find all the numeric differences between the old db rec
    and the current rec we scraped from the site
    """
    tests = [
        'hits', 'kudos',
        'comments', 'bookmarks', 'ref']
    current_dict = current_rec
    db_dict = db_rec.__dict__
    changed = []
    for value_key in tests:
        if report_gen.compare_and_print(
                current_rec["title"],
                value_key,
                current_dict,
                db_dict) > 0:
            setattr(db_rec, value_key, current_dict[value_key])
            changed.append(value_key)
    return changed


def main(db="dbs/readme.db"):
    """
    Main reader for ao3. Start with first page, then see how many pages.
    Get stats on each page.
    Compare with old stats, if any. Report deltas.
    """

    firefox_profile_folder = read_firefox_cookies.get_profile_folder()
    cjar = read_firefox_cookies.get_cookie_jar(firefox_profile_folder)

    if cjar is False:
        sys.exit()

    # Try to make connections less noisy here.
    logging.getLogger(
        'urllib3.connectionpool').setLevel(logging.ERROR)

    try:
        works_page = "https://archiveofourown.org/users/RockSunner/works"
        with PageGetter(cookie_jar=cjar) as pgetter:
            # Note: will need to be able to plug in a name.
            tree = pgetter.get_page(works_page)
            find_navigation = \
                etree.XPath('//ol[@class = "pagination actions"]/li/a')
            page_nums = find_navigation(tree)
            keys = []
            for res in page_nums:
                res_t = res.text_content()
                if RepresentsInt(res_t):
                    keys.append(int(res_t))
                else:
                    break

            scraper = Ao3Scraper()
            recs = []

            scraper.parse_tree(tree, recs)

            for key in keys:
                payload = {"page": key}
                tree = pgetter.get_page(works_page, payload)
                scraper.parse_tree(tree, recs)

            report_gen = ReportGen("A03")
            with ReadMeDb(db, echo=False) as read_db:
                for rec in recs:
                    story = read_db.get_or_create_ao3_story(rec["title"])
                    changed = compare_ao3_rec(story, rec, report_gen)
                    if "kudos" in changed:
                        eprint("Could look up kudos here")
                report_gen.print_report()
                read_db.set_commit_flag()

            pgetter.stop_sleep()

    except ConnectionRefusedError as exc:
            eprint("ConnectionRefused to archiveofourown.org", exc)
    except ConnectionAbortedError as exc:
            eprint("Connection problem", exc)
    except Exception as exc:
        eprint("Cannot connect to archiveofourown.org", exc)


# Do an update from the current fanfiction.net to our db.
if __name__ == "__main__":
    main()
