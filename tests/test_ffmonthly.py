# -*- coding: utf-8 -*-

from context import dyrm

"""Tests for Do You Read Me."""
import os
import unittest
from mock import patch, MagicMock
from dyrm.readme_db import ReadMeDb
from dyrm.ffgetter import PageGetter, FanfictionGetter, FanfictionScraper
from dyrm.ffgetter import MonthCaption, TitleRec
# import dyrm.ffmonthly
from dyrm.ffmonthly import MonthlyDataTree, MonthlySetup
import requests
import types
from requests import Session, Response
from lxml import html


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


class FFMonthlyTestCase(unittest.TestCase):
    """ Mocked unit tests """

    # pylint: disable=too-many-instance-attributes

    def setUp(self):
        self.cjar = MagicMock()
        self.eyes_text = file_to_string("test_story_eyes.php")
        self.eyes_text_08 = file_to_string("test_story_eyes08.php")
        self.chapters_text = file_to_string("test_chapter_page.php")
        # self.legacy_text = file_to_string("test_story.php")

        chapter_info = file_to_string("chapter_out2.txt")
        self.chapter_dict = chapter_info
        self.chapter_updates = [
            (2271485, 'A Series of Incredible Events'),
            (10913419, 'A Series of Unfortunate Falls'),
            (3381192, 'Artemis Fowl and the House Elf'),
            (11096572, 'Axed'),
            (2677054, 'Beginning to be Bad'),
            (11107876, 'Biding My Time'),
            (11566628, "Billendin's Game"),
            (10894080, 'Billiffany'),
            (10982066, 'Book Exchange'),
            (11651321, 'Bubble Trouble'),
            (10266662, 'Cousin Who?'),
            (10357978, 'Crooked House'),
            (10762180, 'Defying Gravity Falls'),
            (11478967, 'Developing Chalcedony'),
            (9198900, 'Disk Mania'),
            (11403754, 'Dream Scrape'),
            (11498655, 'Dueling For Her'),
            (10790320, 'Erasure'),
            (7412191, 'Flim Flammed'),
            (1483583, 'Ghost Story'),
            (10903681, 'Gideon Erased'),
            (11825536, 'Gravitated Away'),
            (9306527, 'Gravity Incorporated'),
            (10756448, 'Gravity Universe'),
            (11237042, 'Gravmanji'),
            (3712210, 'Hallows Not Horcruxes'),
            (11845471, 'Happily Ever After'),
            (10948479, 'Head Line'),
            (1406459, 'Hermione in Ravenclaw'),
            (1403847, 'Home Free'),
            (9205410, 'In Hot Water'),
            (11160999, 'Invisible Wizard'),
            (6804340, "Isabella's Quantum Boogaloo"),
            (10253851, 'Jailhouse Pop Rock'),
            (10250372, 'Lebam the Bicycle Thief'),
            (10303717, 'Lebam the Party Crasher'),
            (10463849, 'Lebam the Rescuer'),
            (11168644, 'Miserable Mabel'),
            (9175019, 'Mystery Reincorporated'),
            (11560297, 'Not Getting Stupid'),
            (7525288, 'Old Meets New'),
            (3976281, 'One Bite'),
            (12099635, 'Oracular'),
            (11068526, 'Panic Room'),
            (11024086, 'Potion Beastly'),
            (11016058, 'Potion Explosion'),
            (11317408, 'Potion Girls'),
            (11685846, 'Potion Harem'),
            (11073002, 'Potion Noir'),
            (11026313, 'Potion Nullified'),
            (11522126, 'Potion Pines'),
            (11121637, 'Potion Pooled'),
            (11029331, 'Potion Power'),
            (11035003, 'Potion Punishment'),
            (11058914, 'Potion Purple'),
            (11042944, 'Potion Revenge'),
            (10968843, 'Potion Triangulated'),
            (11085064, 'Potion Twins'),
            (10848039, 'Potionate'),
            (11934271, 'Potionmageddon'),
            (11111595, 'Pushing It'),
            (317331, 'RanGen 12'),
            (11602745, 'Saving Face'),
            (2343063, 'Series of Incredible Events 2'),
            (2460100, 'Series of Incredible Events 3'),
            (7081368, 'Sphere of Trust'),
            (1458950, 'Spin Ministry'),
            (10883628, "Tambry's In Love"),
            (11114432, 'The Apocalypse Is Now'),
            (2157647, 'The Audacious Author'),
            (9773958, 'The Bad Die Young'),
            (10964550, 'The Big Falls'),
            (3238442, 'The Continuation'),
            (3325749, 'The Count who Would be King'),
            (2637914, 'The Distressing Destiny'),
            (11448393, "The Flight of Dipper's"),
            (6905925, 'The Ghost and the Machine'),
            (9349941, 'The Incredible Robinsons'),
            (2075445, 'The Intractable Interrogator'),
            (2673037, 'The Law is an Ass'),
            (10162894, 'The Life of Domiclese'),
            (10094917, 'The Life of Lebam'),
            (11542541, 'The Llama That Knew Too Much'),
            (11297115, 'The Man Behind the Mystery Shack'),
            (1363662, 'The Other Door'),
            (2634266, 'The Proximate Peril'),
            (317683, 'The War of the Balance'),
            (2673021, 'Volatile'),
            (7064395, 'Walking the Dog Home'),
            (2658844, 'What Else Can I Do?'),
            (1256016, "Yubaba's Night"),
            (11796113, 'Zodiac Prophecy')]
        self.titles = [
            TitleRec(ref=8147532, title='A New Song for Jayne'),
            TitleRec(ref=2271485, title='A Series of Incredible Events'),
            TitleRec(ref=10913419, title='A Series of Unfortunate Falls'),
            TitleRec(ref=3381192, title='Artemis Fowl and the House Elf'),
            TitleRec(ref=4642495, title='Artemis Fowl and the Wizard War'),
            TitleRec(ref=11096572, title='Axed'),
            TitleRec(ref=2677054, title='Beginning to be Bad'),
            TitleRec(ref=11107876, title='Biding My Time'),
            TitleRec(ref=11566628, title="Billendin's Game"),
            TitleRec(ref=10894080, title='Billiffany'),
            TitleRec(ref=10982066, title='Book Exchange'),
            TitleRec(ref=11651321, title='Bubble Trouble'),
            TitleRec(ref=10266662, title='Cousin Who?'),
            TitleRec(ref=10357978, title='Crooked House'),
            TitleRec(ref=10762180, title='Defying Gravity Falls'),
            TitleRec(ref=11478967, title='Developing Chalcedony'),
            TitleRec(ref=9198900, title='Disk Mania'),
            TitleRec(ref=11403754, title='Dream Scrape'),
            TitleRec(ref=11498655, title='Dueling For Her'),
            TitleRec(ref=10790320, title='Erasure'),
            TitleRec(ref=2452230, title='Fiona Hesitates'),
            TitleRec(ref=7412191, title='Flim Flammed'),
            TitleRec(ref=1483583, title='Ghost Story'),
            TitleRec(ref=10903681, title='Gideon Erased'),
            TitleRec(ref=11825536, title='Gravitated Away'),
            TitleRec(ref=9306527, title='Gravity Incorporated'),
            TitleRec(ref=10756448, title='Gravity Universe'),
            TitleRec(ref=11237042, title='Gravmanji'),
            TitleRec(ref=3712210, title='Hallows Not Horcruxes'),
            TitleRec(ref=11845471, title='Happily Ever After'),
            TitleRec(ref=10948479, title='Head Line'),
            TitleRec(ref=1406459, title='Hermione in Ravenclaw'),
            TitleRec(ref=1403847, title='Home Free'),
            TitleRec(ref=9205410, title='In Hot Water'),
            TitleRec(ref=11160999, title='Invisible Wizard'),
            TitleRec(ref=6804340, title="Isabella's Quantum Boogaloo"),
            TitleRec(ref=10253851, title='Jailhouse Pop Rock'),
            TitleRec(ref=2674443, title='Janice Faced'),
            TitleRec(ref=10250372, title='Lebam the Bicycle Thief'),
            TitleRec(ref=10303717, title='Lebam the Party Crasher'),
            TitleRec(ref=10463849, title='Lebam the Rescuer'),
            TitleRec(ref=11168644, title='Miserable Mabel'),
            TitleRec(ref=9175019, title='Mystery Reincorporated'),
            TitleRec(ref=7829061, title='Newton Rules!'),
            TitleRec(ref=11560297, title='Not Getting Stupid'),
            TitleRec(ref=7525288, title='Old Meets New'),
            TitleRec(ref=3976281, title='One Bite'),
            TitleRec(ref=12099635, title='Oracular'),
            TitleRec(ref=11068526, title='Panic Room'),
            TitleRec(ref=11024086, title='Potion Beastly'),
            TitleRec(ref=11016058, title='Potion Explosion'),
            TitleRec(ref=11317408, title='Potion Girls'),
            TitleRec(ref=11685846, title='Potion Harem'),
            TitleRec(ref=11073002, title='Potion Noir'),
            TitleRec(ref=11026313, title='Potion Nullified'),
            TitleRec(ref=11522126, title='Potion Pines'),
            TitleRec(ref=11121637, title='Potion Pooled'),
            TitleRec(ref=11029331, title='Potion Power'),
            TitleRec(ref=11035003, title='Potion Punishment'),
            TitleRec(ref=11058914, title='Potion Purple'),
            TitleRec(ref=11042944, title='Potion Revenge'),
            TitleRec(ref=10968843, title='Potion Triangulated'),
            TitleRec(ref=11085064, title='Potion Twins'),
            TitleRec(ref=10848039, title='Potionate'),
            TitleRec(ref=11934271, title='Potionmageddon'),
            TitleRec(ref=11111595, title='Pushing It'),
            TitleRec(ref=317331, title='RanGen 12'),
            TitleRec(ref=11602745, title='Saving Face'),
            TitleRec(ref=2343063, title='Series of Incredible Events 2'),
            TitleRec(ref=2460100, title='Series of Incredible Events 3'),
            TitleRec(ref=7081368, title='Sphere of Trust'),
            TitleRec(ref=1458950, title='Spin Ministry'),
            TitleRec(ref=10883628, title="Tambry's In Love"),
            TitleRec(ref=11114432, title='The Apocalypse Is Now'),
            TitleRec(ref=2157647, title='The Audacious Author'),
            TitleRec(ref=9773958, title='The Bad Die Young'),
            TitleRec(ref=3617579, title='The Baudelaire Who Lived'),
            TitleRec(ref=10964550, title='The Big Falls'),
            TitleRec(ref=3475039, title='The Cautious Concierge'),
            TitleRec(ref=3238442, title='The Continuation'),
            TitleRec(ref=3325749, title='The Count who Would be King'),
            TitleRec(ref=2637914, title='The Distressing Destiny'),
            TitleRec(ref=3113214, title='The Extraneous End'),
            TitleRec(ref=11448393, title="The Flight of Dipper's"),
            TitleRec(ref=6905925, title='The Ghost and the Machine'),
            TitleRec(ref=9349941, title='The Incredible Robinsons'),
            TitleRec(ref=2075445, title='The Intractable Interrogator'),
            TitleRec(ref=2673037, title='The Law is an Ass'),
            TitleRec(ref=10162894, title='The Life of Domiclese'),
            TitleRec(ref=10094917, title='The Life of Lebam'),
            TitleRec(ref=11542541, title='The Llama That Knew Too Much'),
            TitleRec(ref=11297115, title='The Man Behind the Mystery Shack'),
            TitleRec(ref=1363662, title='The Other Door'),
            TitleRec(ref=2634266, title='The Proximate Peril'),
            TitleRec(ref=1952682, title='The Second Slippery Slope'),
            TitleRec(ref=317683, title='The War of the Balance'),
            TitleRec(ref=2673021, title='Volatile'),
            TitleRec(ref=7064395, title='Walking the Dog Home'),
            TitleRec(ref=2658844, title='What Else Can I Do?'),
            TitleRec(ref=2662609, title='What Else Can I Do Now?'),
            TitleRec(ref=2685228, title='What Will We Do Now?'),
            TitleRec(ref=1256016, title="Yubaba's Night"),
            TitleRec(ref=11796113, title='Zodiac Prophecy')]

    def tearDown(self):
        pass

    @patch('requests.Response', autospec=Response)
    @patch('requests.Session', autospec=Session)
    def test_titles(self, mock_session, mock_response):
        """ Want to know if we can get a list of titles from eyes page """
        mock_response.status_code = requests.codes.ok
        mock_response.text = self.eyes_text
        mock_response.content = self.eyes_text.encode("utf-8")
        mock_session.get.return_value = mock_response
        with PageGetter(mock_session, cookie_jar=self.cjar) as pgetter:
            getter = FanfictionGetter(pgetter)
            eyes_tree = getter.get_story_eyes_tree()
            scraper = FanfictionScraper()
            titles = scraper.get_titles(eyes_tree)
            self.assertEqual(titles, self.titles)

    # @patch('requests.Response', autospec=Response)
    # @patch('requests.Session', autospec=Session)
    # def test_do_story_chapters(self, mock_session, mock_response):
    #     """Want the monthly chapter data for one story """
    #     mtree = MonthlyDataTree("08", "2016")
    #     sref = 2271485
    #     s_title = 'A Series of Incredible Events'
    #     mock_response.status_code = requests.codes.ok
    #     mock_response.text = self.chapters_text
    #     mock_response.content = self.chapters_text.encode("utf-8")
    #     mock_session.get.return_value = mock_response
    #     mock_mcap = MagicMock(autospec=MonthCaption)
    #     mock_mcap.month = "08"
    #     mock_mcap.year = "2016"
    #     with PageGetter(mock_session, cookie_jar=self.cjar) as pgetter:
    #         getter = FanfictionGetter(pgetter)
    #         mcap2, _, _, _ = \
    #             mtree.check_story_chapters(sref, s_title, getter, mock_mcap)
    #         report = mtree.get_report()
    #         self.assertEqual(report.get_report_len(), 1)
    #         self.assertEqual(mcap2.year, "2016")

    # def test_monthly_updates(self):
    #     """ Want to know if I can drive monthly data directly,
    #         when the database access is cleanly factored out.
    #         (Law of Demeter)
    #     """
    #     scraper = FanfictionScraper()
    #     content = self.eyes_text.encode("utf-8")
    #     tree = html.fromstring(content)
    #     getter = MagicMock(autospec=FanfictionGetter)
    #     story_rows = scraper.get_month_story_rows(tree)
    #     mtree = MonthlyDataTree(getter, "08", "2016", self.chapter_dict)
    #     chapter_list = mtree.check_story_updates(story_rows)
    #     self.assertEqual(92, len(chapter_list))

    def test_caption_updates(self):
        """ Want to know if I can update the basic monthly
            totals of views and visitors using the story_eyes
            caption.
        """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        tree = html.fromstring(content)
        mcap = scraper.get_month_caption(tree)
        getter = MagicMock(autospec=FanfictionGetter)
        read_db = MagicMock(autospec=ReadMeDb)
        mock_mtop = types.SimpleNamespace(
            mid=1, day=10, views=101, visitors=101)
        read_db.get_or_create_mtop.return_value = mock_mtop
        my_date = types.SimpleNamespace(mid=1, month=8, year=2016)
        mtree = MonthlyDataTree(getter, my_date, eyes_tree=tree)
        new_tree = mtree.check_caption_updates(mcap, read_db)
        self.assertEqual(new_tree.visitors, mcap.visitors)
        self.assertEqual(new_tree.views, mcap.views)
        mcap_report = mtree.get_monthly_report()
        self.assertEqual(1, mcap_report.get_report_len())

    # def test_monthly_updates_on_empty(self):
    #     """ Want to know if I can drive monthly data directly,
    #         when the database access is cleanly factored out.
    #         This time on an empty month start
    #     """
    #     scraper = FanfictionScraper()
    #     content = self.eyes_text.encode("utf-8")
    #     tree = html.fromstring(content)
    #     story_rows = scraper.get_month_story_rows(tree)
    #     mtree = MonthlyDataTree("08", "2016")
    #     chapter_list = mtree.check_story_updates(story_rows)
    #     self.assertEqual(92, len(chapter_list))

    def test_is_bootstrap(self):
        """ See if an on-empty database statup tests correctly """
        bogus_db = 'bogus3.db'
        _safe_remove(bogus_db)
        with ReadMeDb(bogus_db) as read_db:
            msetup = MonthlySetup(read_db)
            self.assertEqual(True, msetup.is_bootstrap())

    # @patch('requests.Response', autospec=Response)
    # @patch('requests.Session', autospec=Session)
    # def test_check_chapter_updates(self, mock_session, mock_response):
    #     """Want the rows from the monthly top-level story visits table """
    #     mock_response.status_code = requests.codes.ok
    #     mock_response.text = self.eyes_text
    #     mock_response.content = self.eyes_text.encode("utf-8")
    #     mock_session.get.return_value = mock_response
    #     mock_mcap = MagicMock(autospec=MonthCaption)
    #     mock_mcap.month = "08"
    #     mock_mcap.year = "2016"
    #     with PageGetter(mock_session, cookie_jar=self.cjar) as pgetter:
    #         getter = FanfictionGetter(pgetter)
    #         eyes_tree = getter.get_story_eyes_tree()
    #         scraper = FanfictionScraper()
    #         story_rows = scraper.get_month_story_rows(eyes_tree)
    #         bogus_db = 'bogus2.db'
    #         _safe_remove(bogus_db)
    #         with ReadMeDb(bogus_db) as read_db:
    #             _, chapter_list = ffmonthly.check_chapter_updates(
    #                 mock_mcap, story_rows, read_db)
    #             # print(rec)
    #             self.assertEqual(len(chapter_list), len(self.chapter_updates))
    #             self.assertEqual(chapter_list, self.chapter_updates)


if __name__ == '__main__':
    unittest.main()
