#!/usr/bin/env python

"""
Screen-scraper for writers of fan fiction.
Auxillary for getting user favs and follows.
"""
import sys
import dyrm.read_firefox_cookies as read_firefox_cookies
from dyrm.ffgetter import PageGetter, FanfictionGetter, FanfictionScraper
from dyrm.readme_db import ReadMeDb, FavMe, FollowMe
from dyrm.reportgen import ReportGen


def ff_details_to_db(detail, code, session):
    """ Record fav/follow changes in db """
    if detail == "fav added":
        efav = session.query(FavMe).filter_by(code=code).first()
        if not efav:
            new_fav = FavMe(code=code)
            session.add(new_fav)
    elif detail == "follow added":
        efollow =\
            session.query(FollowMe).filter_by(code=code).first()
        if not efollow:
            new_follow = FollowMe(code=code)
            session.add(new_follow)
    elif detail == "fav removed":
        fav = session.query(FavMe).filter_by(code=code).first()
        if fav:
            session.delete(fav)
    elif detail == "follow removed":
        follow =\
            session.query(FollowMe).filter_by(code=code).first()
        if follow:
            session.delete(follow)


def report_ff_change(
        detail, user_set, report_gen,
        read_db, web_dict=None):
    """ Message to log """

    # pylint: disable=too-many-arguments

    if web_dict is None:
        web_dict = {}
    message = "{0} ".format(detail)
    title = "Me"

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

        ff_details_to_db(detail, code, read_db.session)


def get_db_fav_users(read_db):
    """
    Each fav list that we want to change will require a
    fetch of the current db details.
    """
    ffset = set()
    ff_recs = read_db.get_favs_for_me()
    if ff_recs:
        ffset = {int(x.code) for x in ff_recs}
    ff_recs = None
    return ffset


def get_db_follow_users(read_db):
    """
    Each follow list that we want to change will require a
    fetch of the current db details.
    """
    ffset = set()
    ff_recs = read_db.get_follows_for_me()
    if ff_recs:
        ffset = {int(x.code) for x in ff_recs}
    ff_recs = None
    return ffset

def get_fav_users(getter, scraper):
    """
    Each fav list that we want to change will require a
    fetch of the current web details.
    """
    fav_tree = getter.get_favme()
    fav_recs = scraper.get_users(fav_tree)
    ffset = set()
    ffdict = dict()
    if fav_recs:
        ffset = {int(x.id) for x in fav_recs}
        ffdict = {int(x.id): x.alias for x in fav_recs}
    return ffset, ffdict


def get_follow_users(getter, scraper):
    """
    Each follow list that we want to change will require a
    fetch of the current web details.
    """
    follow_tree = getter.get_followme()
    follow_recs = scraper.get_users(follow_tree)
    ffset = set()
    ffdict = dict()
    if follow_recs:
        ffset = {int(x.id) for x in follow_recs}
        ffdict = {int(x.id): x.alias for x in follow_recs}
    return ffset, ffdict


def print_favs(getter, scraper, read_db, report_gen):
    """ Compare user favs, latest to db """
    fav_set, fav_dict = get_fav_users(getter, scraper)
    ufav_set = get_db_fav_users(read_db)

    added = fav_set - ufav_set
    removed = ufav_set - fav_set
    if added:
        report_ff_change(
            "fav added", added, report_gen,
            read_db, fav_dict)
    if removed:
        report_ff_change(
            "fav removed", removed, report_gen,
            read_db)


def print_follows(getter, scraper, read_db, report_gen):
    """ Compare user follows, latest to db """

    follow_set, follow_dict = get_follow_users(getter, scraper)
    ufollow_set = get_db_follow_users(read_db)

    added = follow_set - ufollow_set
    removed = ufollow_set - follow_set
    if added:
        report_ff_change(
            "follow added", added, report_gen,
            read_db, follow_dict)
    if removed:
        report_ff_change(
            "follow removed", removed, report_gen,
            read_db)


def main():
    """ Main driver """

    firefox_profile_folder = read_firefox_cookies.get_profile_folder()
    cjar = read_firefox_cookies.get_cookie_jar(firefox_profile_folder)

    if cjar is False:
        sys.exit()

    scraper = FanfictionScraper()
    with ReadMeDb(echo=False) as read_db:
        try:
            with PageGetter(cookie_jar=cjar) as pgetter:
                getter = FanfictionGetter(pgetter)

                report_gen = ReportGen('Me')
                print_favs(getter, scraper, read_db, report_gen)
                print_follows(getter, scraper, read_db, report_gen)
                report_gen.print_report()

            # with ReadMeDb(echo=False) as read_db:
            #     favs_to_update, follows_to_update = \
            #         dyrm.do_legacy_story_page(
            #             getter, read_db, scraper, report_gen)
            #     dyrm.check_fav_follow_changes(
            #         favs_to_update, follows_to_update,
            #         read_db, getter, report_gen)
            #     read_db.set_commit_flag()

            pgetter.stop_sleep()

        except ConnectionRefusedError:
            print("Need to be logged in to fanfiction.net")
        except ConnectionAbortedError as exc:
            print("Connection problem", exc)

        read_db.set_commit_flag()


# Test the script, see if we are logged into fanfiction.net
if __name__ == "__main__":
    main()
