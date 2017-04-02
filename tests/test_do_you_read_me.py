# -*- coding: utf-8 -*-

from context import dyrm

"""Tests for Do You Read Me."""
import os
import unittest
from mock import patch, MagicMock
from dyrm.readme_db import ReadMeDb
from dyrm.ffgetter import PageGetter, FanfictionGetter
import dyrm.do_you_read_me as do_you_read_me
from dyrm.reportgen import ReportGen
import requests
from requests import Session, Response


def _safe_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def file_to_string(filename):
    """ file contents into a string """
    data = ""
    try:
        with open(filename, 'r') as myfile:
            data = myfile.read()
    except IOError:
        pass
    return data


class DoYouReadMeTestCase(unittest.TestCase):
    """ Mocked unit tests """

    def setUp(self):
        self.cjar = MagicMock()
        self.legacy_text = file_to_string("test_story.php")
        self.part_favs_text = file_to_string("part_favs.php")

    def tearDown(self):
        pass

    @patch('requests.Response', autospec=Response)
    @patch('requests.Session', autospec=Session)
    def test_do_legacy(self, mock_session, mock_response):
        """ Want the results from the legacy page """
        mock_response.status_code = requests.codes.ok
        mock_response.text = self.legacy_text
        mock_response.content = self.legacy_text.encode("utf-8")
        mock_session.get.return_value = mock_response
        with PageGetter(mock_session, cookie_jar=self.cjar, delay=0.1) as pgetter:
            getter = FanfictionGetter(pgetter)
            bogus_db = 'bogus2.db'
            _safe_remove(bogus_db)
            with ReadMeDb(bogus_db) as read_db:
                repgen = ReportGen('Legacy', silent=True)
                do_you_read_me.do_legacy_story_page(
                    getter, read_db, report_gen=repgen)
                self.assertEqual(103, repgen.get_report_len())

    @patch('requests.Response', autospec=Response)
    @patch('requests.Session', autospec=Session)
    def test_fav_follow_changes(self, mock_session, mock_response):
        """ see if we can detect the addition of a favorite """
        mock_response.status_code = requests.codes.ok
        mock_response.text = self.part_favs_text
        mock_response.content = self.part_favs_text.encode("utf-8")
        mock_session.get.return_value = mock_response
        favs_to_update = [2271485]
        follows_to_update = []
        with PageGetter(mock_session, cookie_jar=self.cjar, delay=0.1) as pgetter:
            getter = FanfictionGetter(pgetter)
            bogus_db = 'readme.db'
            with ReadMeDb(bogus_db) as read_db:
                repgen = ReportGen('Legacy', silent=False)
                do_you_read_me.check_fav_follow_changes(
                    favs_to_update, follows_to_update, read_db, getter, repgen)
                self.assertEqual(0, repgen.get_report_len())
                self.assertEqual(1, mock_session.get.call_count)


if __name__ == '__main__':
    unittest.main()
