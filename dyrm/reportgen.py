#!/usr/bin/env python

"""
Change report generator
"""

import re
import logging
from collections import defaultdict


def uncomma(num_str):
    """
    Remove commas and (later) fix other conversion issues
    for numbers from fanfiction.net pages.
    """
    num_str2 = num_str.strip()
    if num_str2 == '':
        return 0
    return int(re.sub(',', '', num_str2))


def print_divider():
    """ Dividing line between sections of output """
    logger = logging.getLogger(__name__)
    logger.info("-" * 10)


class ReportGen:
    """
    Take in change information and generate
    an output report.
    """

    def __init__(self, report_title, silent=False, catchup=True):
        self.report = defaultdict(list)
        self.report_title = report_title
        self.silent = silent
        self.false_return = 0
        if catchup:
            self.false_return = 1
        self.used_keys = set()

    def line_to_report(self, key, line):
        """
        Add a line to be printed in the change report.
        It will be printed sorted by title.
        """
        self.report[key].append(line)

    def compare_totals_by_country(
            self, country, prefix,
            val_key, grp, old_grp):
        """
        At the monthly level, record changes in the story views and visitors.
        """

        # pylint: disable=too-many-arguments

        val = grp[val_key]
        old_val = old_grp[prefix + val_key]
        if val != old_val:
            val_delta = val - old_val
            self.line_to_report(
                "Monthly",
                "country '%s': %s %d to %d (delta %d)" %
                (country, val_key, old_val, val, val_delta))
            return 1
        return self.false_return

    def compare_story_by_country(
            self, s_title, country, prefix, val_key, grp, old_grp):
        """
        At the story level, record changes in the story views and visitors.
        """

        # pylint: disable=too-many-arguments

        val = grp[val_key]
        old_val = old_grp[prefix + val_key]
        if val != old_val:
            val_delta = val - old_val
            self.line_to_report(
                s_title,
                "country '%s': %s %d to %d (delta %d)" %
                (country, val_key, old_val, val, val_delta))
            return 1
        return self.false_return

    def compare_and_print_ctry_chapter(
            self, country, s_title, ch_num,
            ch_title, prefix, val_key, grp, old_grp):
        """
           Title of the story, for indexing
           Number of the chapter
           Title of the chapter
           Country name
           val-key, as before it's the key for comparison (views or visitors)
           prefix not needed now
        """

        # pylint: disable=too-many-arguments

        val = grp[val_key]
        old_val = old_grp.get(prefix + val_key, 0)
        if val != old_val:
            val_delta = val - old_val
            self.line_to_report(
                s_title,
                "chapter %d: '%s' for '%s' %s %d to %d (delta %d)" %
                (ch_num, ch_title, country, val_key, old_val, val, val_delta))
            return 1
        return self.false_return

    def compare_and_print_chapter(
            self, s_title, ch_num, ch_title, prefix, val_key, grp, old_grp):
        """
        This needs to be a deeper and more subtle version of the one below.
        The title I will index to is not the same as the title of the item.
        There is a depth of details as well, like the chapter number and
        sometimes the country. This will take considerable new work.

           Title of the story, for indexing
           Number of the chapter
           Title of the chapter
           Country name, if this is a by-country update.
           val-key, as before it's the key for comparison (views or visitors)
           prefix was 'm_' and for chapters I will want 'c_'
        """

        # pylint: disable=too-many-arguments

        val = grp[val_key]
        old_val = old_grp.get(prefix + val_key, 0)
        if val != old_val:
            val_delta = val - old_val
            self.line_to_report(
                s_title,
                "chapter %d: '%s' %s %d to %d (delta %d)" %
                (ch_num, ch_title, val_key, old_val, val, val_delta))
            return 1
        return 0

    def compare_and_print(
            self, title, val_key, grp, old_grp, prefix="", extra=""):
        """
        Compare old and new values, recording a change
        line for later printing
        """

        # pylint: disable=too-many-arguments

        val = grp[val_key]
        old_val = old_grp.get(prefix + val_key, 0)
        if val != old_val:
            val_delta = val - old_val
            self.line_to_report(
                title,
                "'%s' %s%s %d to %d (delta %d)" %
                (title, extra, val_key, old_val, val, val_delta))
        if val != old_val:
            return 1
        return 0

    def set_catchup(self, catchup):
        self.false_return = 0
        if catchup:
            self.false_return = 1

    def get_report_len(self):
        """ Get the length of the report """
        return len(self.report.keys())

    def print_keyed_section(self, key):
        """ Print one section of a report, by the key (usually title) """
        if key in self.used_keys:
            return
        self.used_keys.add(key)
        if self.report[key]:
            logger = logging.getLogger(__name__)
            if key not in self.report[key][0]:
                # Title if not there
                logger.info(key)
            for line in self.report[key]:
                logger.info(line)

    def print_report(self):
        """ Print out a sorted report of the changes collected """
        if not self.silent:
            for key in sorted(self.report):
                self.print_keyed_section(key)
            print_divider()


def main():
    """ Write a simple report"""
    report = ReportGen("Test report")
    report.line_to_report(2, "Test line 2")
    report.line_to_report(1, "Test line 1")
    report.print_report()


# Do an update from the current fanfiction.net to our db.
if __name__ == "__main__":
    main()
