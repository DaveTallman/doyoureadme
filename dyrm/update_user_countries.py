#!/usr/bin/env python

"""
Screen-scraper to get country information from
user profile pages.
"""

# import sys
import re
from dyrm.ffgetter import PageGetter, FanfictionGetter
from dyrm.readme_db import ReadMeDb
import requests
from contextlib import closing

def get_country(user, session, flag_pattern):
    """
    Get the country information, which will be near the start
    on a flag title, if present.

    User profiles can be gigantic, so use streaming.
    """
    page = "https://www.fanfiction.net/u/" + str(user)
    country = ""
    with closing(session.get(page, timeout=10.0, stream=True)) as r:
        lines = 0;
        for rline in r.iter_lines(chunk_size=10):
            lines += 1
            rstr = repr(rline)
            if rstr.find('Joined <sp') > 0:
                match = re.search(flag_pattern, rstr)
                if match:
                    country = match.group(1)
                break
            if lines > 600:
                break
    return country


def main(userid=None):
    """
    Find users where the country is 'Unknown' and look up
    the country flag on their profile pages.
    """
    # import pdb; pdb.set_trace()
    with ReadMeDb(echo=False) as read_db:
        read_db.set_commit_flag()

        if userid:
            users = read_db.find_users_with_code(userid)
        else:
            users = read_db.find_users_with_country("Unknown")
        if not users:
            return

        session = requests.Session()
        flag_pattern = re.compile(r"""
        ABSMIDDLE
        .*?
        title=
        \\?'
        ([A-Za-z ]+)
        \\?'
        """, re.VERBOSE)
        try:
            for user in users:
                country = get_country(user.code, session, flag_pattern)
                alias = str(user.code)
                if user.aliases:
                    alias = user.aliases[0].name
                print(
                    "Updating user '{0}' ({1}) with country '{2}'".format(
                        alias, str(user.code), country))
                user.country = country

        except ConnectionRefusedError:
            print("Connection refused")
            return
        except ConnectionAbortedError as esc:
            print("Connection problem", esc)
            return

# Do an update from the current fanfiction.net to our db.
if __name__ == "__main__":
    main()
