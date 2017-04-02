#!/usr/bin/env python

"""
Page getter for Fanfiction.net and ao3
"""
from dyrm import update_user_countries


def main():
    print("user countries")
    update_user_countries.main()


# Test the script, see if we are logged into fanfiction.net
if __name__ == "__main__":
    main()
