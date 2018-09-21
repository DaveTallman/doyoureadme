#!/usr/bin/env python

"""
Get cookies from Firefox.
"""

import sys
import os


FTSTR = ["FALSE", "TRUE"]


def get_cookie_jar(profile_folder):
    """
    Original Author: Noah Fontes nfontes AT cynigram DOT com
    Original URL:
      http://blog.mithis.net/archives/python/90-firefox3-cookies-in-python
    License: MIT

    Maintainer: Dotan Cohen
    * Ported to Python 3
    * Support cookies from recovery.js
    * Accept profile folder as input parameter instead of sqlite filename
    """

    import http.cookiejar
    from io import StringIO

    strio = StringIO()
    strio.write("""\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
""")

    if read_cookies_db(profile_folder, strio) is False:
        return False

    # read_sessions_file(profile_folder, strio)

    strio.seek(0)
    cookie_jar = http.cookiejar.MozillaCookieJar()
    cookie_jar._really_load(strio, '', True, True)

    return cookie_jar


def read_cookies_db(profile_folder, strio):
    """
    Read the Firefox cookies database.
    """

    import os
    import sqlite3

    sql_file = os.path.join(profile_folder, 'cookies.sqlite')

    try:
        con = sqlite3.connect(sql_file)
    except sqlite3.OperationalError:
        return False

    cur = con.cursor()
    cur.execute(
        "SELECT host, path, isSecure, expiry, name, value FROM moz_cookies")

    for f_item in cur.fetchall():
        strio.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            f_item[0], FTSTR[f_item[0].startswith('.')], f_item[1],
            FTSTR[f_item[2]], f_item[3], f_item[4], f_item[5]))
    return True


def read_sessions_file(profile_folder, strio):
    """
    Read from the active sessions file.
    Firefox must be up for this to work.
    """

    import json
    import os
    import time

    sessions_file = os.path.join(
        profile_folder,
        'sessionstore-backups/recovery.js')

    try:
        sessions_input = open(sessions_file, 'r')
    except FileNotFoundError:
        return

    sessions_data = json.loads(sessions_input.read())

    for win in sessions_data['windows']:
        for c_item in win['cookies']:

            # Required Keys: host, path, value, name
            # Optional keys: httponly
            # Missing Keys: expiry, secure

            # This does not seem to be used in the output file format
            c_item['httponly'] = 0
            if 'httponly' in c_item and c_item['httponly'] is True:
                c_item['httponly'] = 1

            # I could find no instance of this actually being used.
            # I am only guessing that it exists.
            c_item['secure'] = 0
            if 'secure' in c_item and c_item['secure'] is True:
                c_item['secure'] = 1

            # This field is needed, even though it doesn't seem to be
            # available in the JSON
            c_item['expiry'] = int(time.time() + 84600)

            strio.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                c_item['host'],
                FTSTR[c_item['host'].startswith('.')],
                c_item['path'],
                FTSTR[c_item['secure']],
                c_item['expiry'],
                c_item['name'],
                c_item['value']))


def get_profile_folder():
    """
    Return the Firefox profile folder

    """

    import configparser

    if sys.platform == 'cygwin' or sys.platform == 'win32':
        # Figure out windows/cygwin details
        path = os.path.join(os.environ['APPDATA'], "Mozilla/Firefox/Profiles")
        for dir in os.listdir(path):
            _, file_ext = os.path.splitext(dir)
            if file_ext == ".default":
                profile_name = dir
                break
        profile_folder = os.path.join(path, profile_name)
    else:
        # The following is for Linux
        home_dir = os.path.expanduser('~')
        user_folder = ".mozilla/firefox"
        user_profile_ini = "profiles.ini"
        config = configparser.ConfigParser()
        config.read(os.path.join(home_dir, user_folder, user_profile_ini))
        path = config['Profile0']['Path']
        profile_folder = os.path.join(home_dir, user_folder, path)

    return profile_folder


def main():
    """ Test driver"""
    firefox_profile_folder = get_profile_folder()
    cjar = get_cookie_jar(firefox_profile_folder)

    if cjar is False:
        eprint("Failed to get a cookie jar.")
        sys.exit()
    print("Got the cookie jar")


# Test the script, see if we are logged into fanfiction.net
if __name__ == "__main__":
    main()

# Old code for reference:

# def sqlite2cookie(filename):
#     from cStringIO import StringIO
#     from pysqlite2 import dbapi2 as sqlite

#     con = sqlite.connect(filename)

#     cur = con.cursor()
#     cur.execute(
#         "select host, path, isSecure, expiry, name, value from moz_cookies")

#     ftstr = ["FALSE", "TRUE"]

#     s = StringIO()
#     s.write("""\
# # Netscape HTTP Cookie File
# # http://www.netscape.com/newsref/std/cookie_spec.html
# # This is a generated file!  Do not edit.
# """)
#     for item in cur.fetchall():
#         s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
#             item[0], ftstr[item[0].startswith('.')], item[1],
#             ftstr[item[2]], item[3], item[4], item[5]))

#     s.seek(0)

#     cookie_jar = cookielib.MozillaCookieJar()
#     cookie_jar._really_load(s, '', True, True)
#     return cookie_jar
