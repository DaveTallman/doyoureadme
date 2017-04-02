#!/usr/bin/env python

"""
Screen-scraper for writers of fan fiction who want to keep
up to date on the hits their stories are getting.
"""

import sys
import logging
# import dyrm.read_firefox_cookies
from dyrm.eprint import eprint
from dyrm.ffgetter import PageGetter, FanfictionGetter, FanfictionScraper
from dyrm.readme_db import ReadMeDb, Favs, Follows
from dyrm.reportgen import ReportGen

# Since the monthly structure is now going to be its own thing,
# probably want it in a class that can hold new and old monthly recs,
# along with report lines. Don't start now, but we do need it.


def do_legacy_story_page(getter, read_db, scraper=None, report_gen=None):
    """
    Process the legacy story page, "story.php"
    """
    if scraper is None:
        scraper = FanfictionScraper()
    legacy_tree = getter.get_legacy_tree()

    # Make sure all story keys are in place first.
    ff_titles = scraper.get_legacy_titles(legacy_tree)
    compare_titles_to_db(ff_titles, read_db)

    recs = scraper.get_legacy(legacy_tree)
    report_is_new = report_gen is None
    if report_gen is None:
        report_gen = ReportGen('Legacy')
    favs_to_update, follows_to_update = \
        compare_legacy_recs_to_db(recs, read_db, report_gen)
    if report_is_new:
        report_gen.print_report()
    return favs_to_update, follows_to_update


def compare_legacy_recs(db_rec, current_rec, read_db, report_gen):
    """
    Find all the numeric differences between the old db rec
    and the current rec we scraped from the site
    """
    tests = [
        'chaps', 'reviews',
        'views', 'c2s', 'favs', 'alerts']
    current_dict = current_rec._asdict()
    if not db_rec:
        db_rec = read_db.create_empty_legacy(current_rec.ref)
    db_dict = db_rec.__dict__
    for value_key in tests:
        if report_gen.compare_and_print(
                current_rec.title,
                value_key,
                current_dict,
                db_dict, extra="legacy "):
            setattr(db_rec, value_key, current_dict[value_key])


def compare_legacy_recs_to_db(legacy_recs, read_db, report_gen):
    """ Query the database for old information, and compare to the latest """
    legacy_query_dict = read_db.get_legacy_table_dict()
    legacy_rec_dict = dict((x.ref, x) for x in legacy_recs)
    fav_counts = read_db.get_fav_counts()
    fav_dict = dict((x[0], x[1]) for x in fav_counts)
    follow_counts = read_db.get_follow_counts()
    follow_dict = dict((x[0], x[1]) for x in follow_counts)

    for key in legacy_rec_dict.keys():
        compare_legacy_recs(
            legacy_query_dict.get(key, None),
            legacy_rec_dict.get(key), read_db, report_gen)

    # see what favorite and follow lists might be out of date.
    favs_to_update = []
    follows_to_update = []
    for key in legacy_rec_dict.keys():
        rec = legacy_query_dict.get(key, None)
        if rec is not None:
            favs = fav_dict.get(key, 0)
            follows = follow_dict.get(key, 0)
            if rec.favs != favs:
                favs_to_update.append(rec.ref)
            if rec.alerts != follows:
                follows_to_update.append(rec.ref)
    return favs_to_update, follows_to_update


def compare_story_recs(db_rec, current_rec, read_db):
    """ Compare a single story record and get it up to date in the db """
    if not db_rec:
        logging.info("New story '{}'".format(current_rec.title))
        db_rec = read_db.get_or_create_story(
            current_rec.ref, current_rec.title)
    if db_rec.title != current_rec.title:
        logging.info(
            "Changed title '{}' to '{}'".format(
                db_rec.title, current_rec.title))
        db_rec.title = current_rec.title


def compare_titles_to_db(ff_titles, read_db):
    """ Query the database for old story title info, compare to the latest """
    db_stories = read_db.get_stories()
    if not db_stories:
        logging.debug("Doing a mass story insert")
        read_db.batch_insert_stories(ff_titles)
        db_stories = read_db.get_stories()
        return

    ff_titles_dict = dict((x.ref, x) for x in ff_titles)
    db_stories_dict = dict((x.ref, x) for x in db_stories)

    for key in ff_titles_dict.keys():
        compare_story_recs(
            db_stories_dict.get(key, None),
            ff_titles_dict.get(key), read_db)
    return


def get_db_fav_users(ref, read_db):
    """
    Each fav list that we want to change will require a
    fetch of the current db details.
    """
    ffset = set()
    ff_recs = read_db.get_favs_for_story(ref)
    if ff_recs:
        ffset = {int(x.code) for x in ff_recs}
    ff_recs = None
    return ffset


def get_db_follow_users(ref, read_db):
    """
    Each follow list that we want to change will require a
    fetch of the current db details.
    """
    ffset = set()
    ff_recs = read_db.get_follows_for_story(ref)
    if ff_recs:
        ffset = {int(x.code) for x in ff_recs}
    ff_recs = None
    return ffset


def get_web_fav_users(ref, getter, scraper):
    """
    Each fav list that we want to change will require a
    fetch of the current web details.
    """
    fav_tree = getter.get_legacy_part(ref, "favs")
    fav_recs = scraper.get_legacy_part(fav_tree)
    ffset = set()
    ffdict = dict()
    if fav_recs:
        ffset = {int(x.id) for x in fav_recs}
        ffdict = {int(x.id): x.alias for x in fav_recs}
    return ffset, ffdict


def get_web_follow_users(ref, getter, scraper):
    """
    Each follow list that we want to change will require a
    fetch of the current web details.
    """
    follow_tree = getter.get_legacy_part(ref, "alerts")
    follow_recs = scraper.get_legacy_part(follow_tree)
    ffset = set()
    ffdict = dict()
    if follow_recs:
        ffset = {int(x.id) for x in follow_recs}
        ffdict = {int(x.id): x.alias for x in follow_recs}
    return ffset, ffdict


def ff_details_to_db(detail, ref, code, session):
    """ Record fav/follow changes in db """
    if detail == "fav added":
        efav = session.query(Favs).filter_by(ref=ref, code=code).first()
        if not efav:
            new_fav = Favs(ref=ref, code=code)
            session.add(new_fav)
    elif detail == "follow added":
        efollow =\
            session.query(Follows).filter_by(ref=ref, code=code).first()
        if not efollow:
            new_follow = Follows(ref=ref, code=code)
            session.add(new_follow)
    elif detail == "fav removed":
        fav = session.query(Favs).filter_by(ref=ref, code=code).first()
        if fav:
            session.delete(fav)
    elif detail == "follow removed":
        follow =\
            session.query(Follows).filter_by(ref=ref, code=code).first()
        if follow:
            session.delete(follow)


def report_ff_change(
        title, detail, user_set, report_gen,
        read_db, ref, web_dict=None):

    # pylint: disable=too-many-arguments
    """ Message to log """
    if web_dict is None:
        web_dict = {}
    message = "'{0}' {1} ".format(title, detail)
    for code in user_set:
        user = read_db.get_or_create_user(code, "Unknown")
        # This times out too much. Make a separate utility
        # to run periodically.
        # if user.country == "Unknown":
        #     country = getter.get_user_country(code)
        #     user.country = country
        if user.aliases:
            alias = user.aliases[0].name
        else:
            alias = web_dict.get(code, "New User")
            if alias != "New User":
                read_db.get_or_create_alias(code, alias)

        user_part =\
            "'{0}' from '{1}' ({2:d})".format(alias, user.country, code)
        report_gen.line_to_report(title, message + user_part)

        ff_details_to_db(detail, ref, code, read_db.session)


def check_fav_follow_changes(
        favs_to_update, follows_to_update, read_db, getter, report_gen):
    """ For each potential fav/follow update, see what actually changed """

    # pylint: disable=too-many-locals, too-many-arguments

    scraper = FanfictionScraper()
    db_titles = read_db.get_titles_dict()
    for ref in favs_to_update:
        title = db_titles.get(ref, "Unknown")
        web_favs, web_dict =\
            get_web_fav_users(ref, getter, scraper)
        db_favs = get_db_fav_users(ref, read_db)
        added = web_favs - db_favs
        removed = db_favs - web_favs
        if added:
            report_ff_change(
                title, "fav added", added, report_gen,
                read_db, ref, web_dict)
        if removed:
            report_ff_change(
                title, "fav removed", removed, report_gen,
                read_db, ref)

    for ref in follows_to_update:
        title = db_titles.get(ref, "Unknown")
        web_follows, web_dict =\
            get_web_follow_users(ref, getter, scraper)
        db_follows = get_db_follow_users(ref, read_db)
        added = web_follows - db_follows
        removed = db_follows - web_follows
        if added:
            report_ff_change(
                title, "follow added", added, report_gen,
                read_db, ref, web_dict)
        if removed:
            report_ff_change(
                title, "follow removed", removed, report_gen,
                read_db, ref)


def main(db="dbs/readme.db"):
    """
    Goal will be to drive this with a to-do loop/stack.
    The stack will contain commands telling what to do next.
    Possible sequence:
    0) Get legacy counts, to find new stories and chapters for db.
       That may also require updates to chapter keys, but we can
       get those in later steps.
    1) Get current story-eyes, without date spec.
    2) If date not current, add prior month story-eyes to the stack.
       This will be a story-eyes with a prior date.
    3) Find stories that need chapter count updates, and push those.
    4) Find chapters that need updates, and push those.
    5) After old is caught up, start a new month if needed.
       Push that and follow the same tricks to update it.
    6) Periodically also follow user favs.
    7) Do regular updated favs, as seen from legacy.

    """

    # pylint: disable=too-many-locals

    import dyrm.read_firefox_cookies as read_firefox_cookies
    firefox_profile_folder = read_firefox_cookies.get_profile_folder()
    cjar = read_firefox_cookies.get_cookie_jar(firefox_profile_folder)

    if cjar is False:
        sys.exit()

    # Prepare for a command loop
    # commands = deque()
    scraper = FanfictionScraper()

    try:
        with PageGetter(cookie_jar=cjar) as pgetter:
            getter = FanfictionGetter(pgetter)
            with ReadMeDb(echo=False) as read_db:
                # month, year, _, _ =\
                #     exec_story_eyes(getter, scraper, read_db)

                # last_monthly = read_db.get_last_monthly()
                # old_month, old_year = last_monthly.get_month_year()
                # if old_month != month or old_year != year:
                #     catch_up_month(getter, scraper, last_monthly)
                report_gen = ReportGen('Legacy')
                favs_to_update, follows_to_update = \
                    do_legacy_story_page(getter, read_db, scraper, report_gen)

                check_fav_follow_changes(
                    favs_to_update, follows_to_update,
                    read_db, getter, report_gen)

                report_gen.print_report()
                read_db.set_commit_flag()

            pgetter.stop_sleep()

    except ConnectionRefusedError:
        eprint("Need to be logged in to fanfiction.net")
    except ConnectionAbortedError as esc:
        eprint("Connection problem", esc)


# Do an update from the current fanfiction.net to our db.
if __name__ == "__main__":
    main()
