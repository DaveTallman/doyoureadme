#!/usr/bin/env python

"""
Screen-scraper for writers of fan fiction who want to keep
up to date on the hits their stories are getting.

This part is for reading and comparing the monthly story
totals.
"""

import sys
import logging
import dyrm.read_firefox_cookies as read_firefox_cookies
from dyrm.eprint import eprint
from dyrm.ffgetter import PageGetter, FanfictionGetter, FanfictionScraper
from dyrm.readme_db import ReadMeDb
from dyrm.reportgen import ReportGen, print_divider
import dyrm.do_you_read_me as doyouread

# Since the monthly structure is now going to be its own thing,
# probably want it in a class that can hold new and old monthly recs,
# along with report lines. Don't start now, but we do need it.


class MonthlySetup:
    """
    Class to determine one of five cases,
    returning a list of MonthlyDataTree records.
    0) Pure boostrap startup, no prior monthly information.
       One data tree in list. Compare with a new empty record.
    1) Simple startup. Prior exists for this same month.
       One data tree in list. Compare with existing record.
    2) Month cross-over startup. Two trees in the list.
       First compares old month with old data.
       Second compares new month with new data.
    3) Possibly fail to connect. Return an empty list.
    4) Eventually, could allow for a mult-month skip.
    """

    def __init__(self, read_db, catchup=False):
        self.last_month = read_db.get_last_month()
        self.catchup = catchup

    def is_bootstrap(self):
        """
        Check for empty db case -- no prior month data.
        Note: this case is of least use to me, needed when
        this becomes released, if it ever does.
        """
        return self.last_month is None

    def get_data_trees(
            self, read_db, getter,
            scraper, report_gen):
        """ Get both old and new data trees if necessary """

        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals

        if self.is_bootstrap():
            # Do this later, much later.
            return []

        # Current eyes page may have new month
        old_month = self.last_month.month
        old_year = self.last_month.year
        old_mid = self.last_month.mid
        eyes_tree = getter.get_story_eyes_tree()
        mcap = scraper.get_month_caption(eyes_tree)
        if not mcap:
            return []

        month = int(mcap.month)
        year = int(mcap.year)

        if old_month != month or old_year != year:
            logging.debug(
                "Need to catch up for {}/{}".format(
                    old_month, old_year))
            # Build a return case with TWO MonthlyDataTrees!!!!
            new_month = read_db.get_or_create_month(
                month=month, year=year, mid=old_mid+1)
            report_gen.set_catchup(self.catchup)
            mtree = MonthlyDataTree(
                getter, new_month, eyes_tree, report_gen, catchup=self.catchup)
            report_gen0 = ReportGen('Last Month')
            mtree0 = MonthlyDataTree(
                getter, self.last_month, eyes_tree=None, report_gen=None)
            return [mtree0, mtree]
        else:
            # Simple data tree case -- current month is good.
            report_gen.set_catchup(self.catchup)
            mtree = MonthlyDataTree(
                getter, self.last_month,
                eyes_tree, report_gen, catchup=self.catchup)
            return [mtree]


class MonthlyDataTree:
    """
    Manage and update information in the database:
    monthly story and chapter hits at several levels,
    with a breakdown by date and country.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
            self, getter, month_rec,
            eyes_tree=None, report_gen=None,
            monthly_gen=None, catchup=False):

        # pylint: disable=too-many-arguments

        self.month = str(month_rec.month).zfill(2)
        self.year = str(month_rec.year)
        self.mid = month_rec.mid
        self.catchup = catchup

        if eyes_tree is None:
            eyes_tree = getter.get_old_story_eyes_tree(self.month, self.year)
        self.eyes_tree = eyes_tree

        if report_gen is None:
            report_gen = ReportGen(
                "Hits for {}/{}".format(
                    self.month, self.year), catchup=self.catchup)
        self.report_gen = report_gen
        if monthly_gen is None:
            monthly_gen = ReportGen(
                "Monthly changes for {}/{}".format(
                    self.month, self.year), catchup=self.catchup)
        self.monthly_gen = monthly_gen
        self.changed_story_set = set()

    def do_chapter_heirarchy(self, getter, scraper, read_db):
        """ Look for count updates in the monthly stories and chapters """
        mcap, by_date, by_country, story_rows = \
            do_story_eyes(scraper, self.eyes_tree)

        print_date_info(by_date)

        self.check_caption_updates(mcap, read_db)
        self.check_country_updates(by_country, read_db)
        self.get_monthly_report().print_report()
        self.check_story_updates(story_rows, read_db)
        chapter_list = read_db.get_checks_pending()

        # Data per changed chapter
        my_report = self.get_report()
        for sref, title in chapter_list:
            _, _, _, _ =\
                self.check_story_chapters(sref, title, getter, mcap, read_db)
            my_report.print_keyed_section(title)

        read_db.clear_checks_pending()

    def check_caption_updates(self, mcap, read_db):
        """ Check overall counts in the monthly caption """
        top_rec = read_db.get_or_create_mtop(self.mid)
        new_rec = top_rec.__dict__
        changed = 0
        mcap_dict = mcap._asdict()
        changed += self.monthly_gen.compare_and_print(
            "Monthly", "views",
            mcap_dict,
            new_rec, prefix="")
        changed += self.monthly_gen.compare_and_print(
            "Monthly", "visitors",
            mcap_dict,
            new_rec, prefix="")
        if changed > 0:
            top_rec.views = mcap.views
            top_rec.visitors = mcap.visitors

    def check_story_updates(self, story_rows, read_db):
        """ Find out what stories need their chapters checked """

        for story in story_rows:
            # There might be a new story, or the start of a month.
            new_rec = read_db.get_or_create_mstory(self.mid, story.ref)
            new_dict = new_rec.__dict__
            story_dict = story._asdict()

            changed = self.report_gen.compare_and_print(
                story.title, "views",
                story_dict,
                new_dict, prefix="")
            changed = changed + \
                self.report_gen.compare_and_print(
                    story.title, "visitors",
                    story_dict,
                    new_dict, prefix="")
            if changed > 0:
                new_rec.views = story.views
                new_rec.visitors = story.visitors
                read_db.set_check_pending(story.ref)
                self.changed_story_set.add(story.title)

    def check_country_updates(self, by_country, read_db):
        """ Compare top-level country totals for the month """
        for country_rec in by_country:
            country = country_rec.cat
            country_dict = country_rec._asdict()
            old_rec = read_db.get_or_create_mctry(self.mid, country)
            old_dict = old_rec.__dict__
            changed = self.monthly_gen.compare_totals_by_country(
                country, "", "views",
                country_dict, old_dict)
            changed += self.monthly_gen.compare_totals_by_country(
                country, "", "visitors",
                country_dict, old_dict)
            if changed > 0:
                old_rec.views = country_rec.views
                old_rec.visitors = country_rec.visitors

    def check_country_totals_for_story(
            self, sref, s_title, by_country, read_db):
        """
        Compare the by-country view and visitor totals for this story
        with previous totals, if any. Record new totals and add
        lines about any changes to the report.
        """
        for country_rec in by_country:
            country = country_rec.cat
            country_dict = country_rec._asdict()
            old_rec = read_db.get_or_create_mstoryctry(self.mid, sref, country)
            old_dict = old_rec.__dict__
            changed = self.report_gen.compare_story_by_country(
                s_title, country, "", "views",
                country_dict, old_dict)
            changed += self.report_gen.compare_story_by_country(
                s_title, country, "", "visitors",
                country_dict, old_dict)
            if changed > 0:
                old_rec.views = country_rec.views
                old_rec.visitors = country_rec.visitors

    def check_story_chapters(self, sref, s_title, getter, mcap, read_db):
        """
        Process the monthly chapter details for a particular story
        """

        # pylint: disable=too-many-arguments

        payload = {"month": mcap.month, "year": mcap.year}
        ch_tree = getter.get_chapters_tree(sref, payload)
        scraper = FanfictionScraper()
        mcap2 = scraper.get_chapters_mcap(ch_tree)
        by_date, by_country = scraper.get_chapters_visits(ch_tree)
        # Note - at this point the monthly checker has the
        # views and visitors by country for the story.
        # It would be appropriate to store and report changes here.
        # Pass the sref and the by_country to a save/report routine.
        self.check_country_totals_for_story(sref, s_title, by_country, read_db)
        chapter_rows = scraper.get_chapters_rows(ch_tree)
        for chapter in chapter_rows:
            chapter_rec = read_db.get_or_create_chapter(sref, chapter)
            if chapter_rec.title != chapter.title:
                logging.info(
                    "chapter title changed to {}".format(chapter.title))
                chapter_rec.title = chapter.title
            db_rec = read_db.get_or_create_mchap(self.mid, sref, chapter.num)

            changed_recs = []
            compare_chapter_recs(
                db_rec, s_title, chapter, self.report_gen, changed_recs)
            for chapter in changed_recs:
                self.do_single_chapter(
                    chapter, sref, s_title, getter, scraper, read_db, mcap)
        return (mcap2, by_date, by_country, chapter_rows)

    def do_single_chapter(
            self, chapter, sref, s_title, getter, scraper, read_db, mcap):
        """ Get chapter by chapter changes """
        single_tree = getter.get_chapter_single(
            chapter.ch_ref, month=mcap.month, year=mcap.year)
        by_ch_country = scraper.get_chapter_single(single_tree)
        for ch_country_rec in by_ch_country:
            country = ch_country_rec.cat
            db_ch_rec = read_db.get_or_create_chapctry(
                self.mid, sref, chapter.num, country)
            compare_chap_country_recs(
                ch_country_rec, s_title,
                db_ch_rec, chapter, self.report_gen)

    def get_report(self):
        """ Access report """
        return self.report_gen

    def get_monthly_report(self):
        """ Access separate initial monthly report """
        return self.monthly_gen

    def get_changed_story_set(self):
        """ Get the set of changed stories """
        return self.changed_story_set


def print_story_rows(story_rows):
    """
    Print the records in the story table.
    They give hit counts for a month.
    """
    for row in story_rows:
        logging.info(
            "%s / %s / %s / %s / %s"
            % (row.title,
               row.words,
               row.views,
               row.visitors,
               row.ref))
    print_divider()


def compare_chap_country_recs(
        current_rec, s_title, db_rec, chapter, report_gen):
    """ Find numeric differences at the country chapter level """
    country = current_rec.cat
    current_dict = current_rec._asdict()
    db_dict = db_rec.__dict__
    if report_gen.compare_and_print_ctry_chapter(
            country,
            s_title,
            int(chapter.num),
            chapter.title,
            "",
            'views',
            current_dict, db_dict):
            db_rec.views = current_dict['views']
    if report_gen.compare_and_print_ctry_chapter(
            country,
            s_title,
            int(chapter.num),
            chapter.title,
            "",
            'visitors',
            current_dict, db_dict):
            db_rec.visitors = current_dict['visitors']


def compare_chapter_recs(
        db_rec, s_title, current_rec, report_gen, changed_recs):
    """
    Find all the numeric differences between the old db rec
    and the current chapter rec we scraped from the site
    """
    tests = [
        'views', 'visitors']
    current_dict = current_rec._asdict()
    db_dict = db_rec.__dict__
    changed = False
    for value_key in tests:
        if report_gen.compare_and_print_chapter(
                s_title,
                int(current_rec.num),
                current_rec.title,
                "",
                value_key,
                current_dict, db_dict):
            setattr(db_rec, value_key, current_dict[value_key])
            changed = True

    if changed:
        changed_recs.append(current_rec)


def do_story_eyes(scraper, eyes_tree, mtop=None):
    """
    Process the starting page, "story_eyes.php"
    Payload allows us to redirect to an older month page,
    which we will sometimes need for catching up on the
    month transition.
    """
    mcap = scraper.get_month_caption(eyes_tree)
    if mcap:
        logging.info(
            "%s/%s views: %s visitors %s" %
            (mcap.month, mcap.year, mcap.views,
             mcap.visitors))
        if mtop:
            mtop.views = int(mcap.views)
            mtop.visitors = int(mcap.visitors)
    else:
        logging.debug("Did not find month string")
        sys.exit()

    print_divider()

    # This will give us two charts, one by date and one by country
    by_date, by_country = scraper.get_monthly_visits(eyes_tree)

    # Get the top-level block of story counts for the month
    story_rows = scraper.get_month_story_rows(eyes_tree)

    return (mcap, by_date, by_country, story_rows)


def print_date_info(by_date):
    """ print results from date and country visitor tables """
    logging.info("Date\tViews\tVisitors")
    for vcount in by_date[0:1]:
        logging.info(
            "%s\t%s\t%s" % (vcount.cat, vcount.views, vcount.visitors))
    print_divider()


def main(db, catchup=False, nomonth=False):
    """ Main driver """

    # pylint: disable=too-many-locals, too-many-statements

    import datetime
    now = datetime.datetime.now()
    logging.info('{0:%Y-%m-%d %H:%M:%S}'.format(now))

    firefox_profile_folder = read_firefox_cookies.get_profile_folder()
    cjar = read_firefox_cookies.get_cookie_jar(firefox_profile_folder)

    if cjar is False:
        sys.exit()

    scraper = FanfictionScraper()
    report_gen = ReportGen('All')

    # Legacy part first, hoping to deal with slow timeouts, etc.
    legacy_error = False
    try:
        with PageGetter(cookie_jar=cjar) as pgetter:
            getter = FanfictionGetter(pgetter)

            with ReadMeDb(db, echo=False) as read_db:
                favs_to_update, follows_to_update = \
                    doyouread.do_legacy_story_page(
                        getter, read_db, scraper, report_gen)
                doyouread.check_fav_follow_changes(
                    favs_to_update, follows_to_update,
                    read_db, getter, report_gen)
                read_db.set_commit_flag()

            pgetter.stop_sleep()

    except ConnectionRefusedError:
        eprint("Need to be logged in to fanfiction.net")
        legacy_error = True
    except ConnectionAbortedError as exc:
        eprint("Connection problem", exc)
        legacy_error = True

    if legacy_error or nomonth:
        report_gen.print_report()
        return

    # Now for the monthly records
    with ReadMeDb(db, echo=False) as read_db:
        try:
            with PageGetter(cookie_jar=cjar) as pgetter:
                getter = FanfictionGetter(pgetter)
                msetup = MonthlySetup(read_db, catchup=catchup)
                data_trees = msetup.get_data_trees(
                    read_db, getter, scraper, report_gen)

                # This is supposed to be both regular and catch-up case.
                for mtree in data_trees:
                    mtree.do_chapter_heirarchy(getter, scraper, read_db)

                pgetter.stop_sleep()

        except ConnectionRefusedError:
            eprint("Need to be logged in to fanfiction.net")
        except ConnectionAbortedError as exc:
            eprint("Connection problem", exc)

        read_db.set_commit_flag()

    # Any sections not already printed happen here
    report_gen.print_report()


# Runs the script, checking for changes
if __name__ == "__main__":
    main("readme.db")
