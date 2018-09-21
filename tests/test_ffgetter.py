# -*- coding: utf-8 -*-

from context import dyrm

"""Tests for Do You Read Me."""
import unittest
from dyrm.ffgetter import FanfictionScraper, VisCounter
from dyrm.ffgetter import TitleRec, MonthlyChapterRec
from lxml import html


def file_to_string(filename):
    """ file contents into a string """
    data = ""
    try:
        with open(filename, 'r') as myfile:
            data = myfile.read()
    except IOError:
        pass
    return data


class FanfictionGetterTestCase(unittest.TestCase):
    """ Mocked unit tests, if possible """

    # pylint: disable=too-many-instance-attributes

    def setUp(self):
        self.eyes_text = file_to_string("test_story_eyes.php")
        self.legacy_text = file_to_string("test_story.php")
        self.chapters_text = file_to_string("test_chapter_page.php")
        self.single_text = file_to_string("test_chapter_single.php")
        self.users_text = file_to_string("user_fav.php")
        self.part_favs_text = file_to_string("part_favs.php")
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
        self.chapter_list = [
            MonthlyChapterRec(
                ch_ref=6393657, num=1,
                title='Chapter 1, Bad Beginning',
                words=668, views=12, visitors=12),
            MonthlyChapterRec(
                ch_ref=6398498, num=2,
                title='Chapter 2, Buddy',
                words=1169, views=5, visitors=5),
            MonthlyChapterRec(
                ch_ref=6401855, num=3,
                title='Chapter 3, Box',
                words=639, views=4, visitors=4),
            MonthlyChapterRec(
                ch_ref=6405924, num=4,
                title='Chapter 4, Breaking',
                words=1446, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6412296, num=5,
                title='Chapter 5, Book',
                words=1272, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6417302, num=6,
                title='Chapter 6, Baby',
                words=533, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6422829, num=7,
                title='Chapter 7, Battle',
                words=1685, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6531019, num=8,
                title='Book the 2nd, The RapTile Room',
                words=1239, views=4, visitors=2),
            MonthlyChapterRec(
                ch_ref=6545008, num=9,
                title='Chapter 2, Ringer',
                words=935, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6552293, num=10,
                title='Chapter 3, Riot',
                words=620, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6557175, num=11,
                title='Chapter 4, Return',
                words=1193, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6562410, num=12,
                title='Chapter 1 of Book the 3rd, White Window',
                words=771, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6567767, num=13,
                title='Chapter 2, Window shopping',
                words=1071, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6573214, num=14,
                title='Chapter 3, Wishy Washy',
                words=641, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6576386, num=15,
                title='Chapter 4, War',
                words=1176, views=1, visitors=1)]
        self.ch1_by_country = [
            VisCounter(cat='United States', views=8, visitors=8)
            , VisCounter(cat='United Kingdom', views=2, visitors=2)
            , VisCounter(cat='Australia', views=1, visitors=1)
            , VisCounter(cat='Germany', views=1, visitors=1)]
        self.ch1_by_date = [
            VisCounter(cat='21/Sun', views=0, visitors=0)
            , VisCounter(cat='20/Sat', views=1, visitors=1)
            , VisCounter(cat='19/Fri', views=0, visitors=0)
            , VisCounter(cat='18/Thu', views=0, visitors=0)
            , VisCounter(cat='17/Wed', views=1, visitors=1)
            , VisCounter(cat='16/Tue', views=1, visitors=1)
            , VisCounter(cat='15/Mon', views=0, visitors=0)
            , VisCounter(cat='14/Sun', views=0, visitors=0)
            , VisCounter(cat='13/Sat', views=1, visitors=1)
            , VisCounter(cat='12/Fri', views=0, visitors=0)
            , VisCounter(cat='11/Thu', views=0, visitors=0)
            , VisCounter(cat='10/Wed', views=0, visitors=0)
            , VisCounter(cat='9/Tue', views=0, visitors=0)
            , VisCounter(cat='8/Mon', views=2, visitors=2)
            , VisCounter(cat='7/Sun', views=0, visitors=0)
            , VisCounter(cat='6/Sat', views=0, visitors=0)
            , VisCounter(cat='5/Fri', views=0, visitors=0)
            , VisCounter(cat='4/Thu', views=0, visitors=0)
            , VisCounter(cat='3/Wed', views=2, visitors=2)
            , VisCounter(cat='2/Tue', views=4, visitors=4)
            , VisCounter(cat='1/Mon', views=0, visitors=0)]


    def tearDown(self):
        pass

    def test_get_titles(self):
        """ Want to know if any titles are found on the page """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        ptitles = scraper.get_titles(eyes_tree)
        self.assertTrue(len(ptitles), len(self.titles))
        for i, item in enumerate(ptitles):
            self.assertEqual(self.titles[i], item)

    def test_get_month_year(self):
        """Want the current month and year the ff site is doing """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        month, year = scraper.get_month_year(eyes_tree)
        self.assertEqual(month, "08")
        self.assertEqual(year, "2016")


    def test_get_legacy(self):
        """ Want the results from the legacy page to match our title list"""
        scraper = FanfictionScraper()
        content = self.legacy_text.encode("utf-8")
        legacy_tree = html.fromstring(content)
        legacy = scraper.get_legacy(legacy_tree)
        self.assertEqual(len(legacy), len(self.titles))
        self.assertEqual(legacy[0].title, 'A New Song for Jayne')
        self.assertEqual(legacy[-1].title, 'Zodiac Prophecy')

    def test_get_legacy_titles(self):
        """ Want the results from the legacy page to match our title list"""
        scraper = FanfictionScraper()
        content = self.legacy_text.encode("utf-8")
        legacy_tree = html.fromstring(content)
        legacy = scraper.get_legacy_titles(legacy_tree)
        self.assertEqual(len(legacy), len(self.titles))
        self.assertEqual(legacy[0].title, 'A New Song for Jayne')
        self.assertEqual(legacy[-1].title, 'Zodiac Prophecy')

    def test_get_legacy_part(self):
        """ Get a part of the legacy stats (favs or follows) """
        scraper = FanfictionScraper()
        content = self.part_favs_text.encode("utf-8")
        part_tree = html.fromstring(content)
        favs = scraper.get_legacy_part(part_tree)
        self.assertEqual(17, len(favs))

    def test_month_latest(self):
        """Want the whole month menu """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        rec = scraper.get_month_latest(eyes_tree)
        self.assertEqual("08", rec.month)
        self.assertEqual("2016", rec.year)

    def test_get_month_caption(self):
        """Want the whole month caption """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        mcap = scraper.get_month_caption(eyes_tree)
        self.assertEqual(mcap.month, "08")
        self.assertEqual(mcap.year, "2016")

    def test_get_monthly_visits(self):
        """Want monthly visits by date and country """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        by_date, by_country = scraper.get_monthly_visits(eyes_tree)
        self.assertEqual(len(by_date), 21)
        self.assertEqual(len(by_country), 64)
        self.assertEqual(by_country[0].cat, "United States")
        self.assertEqual(by_country[0].views, 2073)
        self.assertEqual(by_country[0].visitors, 798)
        self.assertEqual(by_date[0].cat, "21/Sun")
        self.assertEqual(by_date[0].views, 35)
        self.assertEqual(by_date[0].visitors, 11)

    def test_get_month_story_rows(self):
        """Want the rows from the monthly story visits table """
        scraper = FanfictionScraper()
        content = self.eyes_text.encode("utf-8")
        eyes_tree = html.fromstring(content)
        story_rows = scraper.get_month_story_rows(eyes_tree)
        self.assertEqual(len(story_rows), len(self.titles))
        self.assertEqual(story_rows[0].title, 'A New Song for Jayne')
        self.assertEqual(story_rows[-1].title, 'Zodiac Prophecy')

    def test_get_story_chapters(self):
        """ Want rows for story chapters """
        scraper = FanfictionScraper()
        content = self.chapters_text.encode("utf-8")
        chapters_tree = html.fromstring(content)
        chapter_rows = scraper.get_chapters_rows(chapters_tree)
        self.assertEqual(len(chapter_rows), len(self.chapter_list))
        for i, item in enumerate(self.chapter_list):
            self.assertEqual(chapter_rows[i].ch_ref, item.ch_ref)
            self.assertEqual(chapter_rows[i].num, item.num)
            self.assertEqual(chapter_rows[i].title, item.title)
            self.assertEqual(chapter_rows[i].words, item.words)
            self.assertEqual(chapter_rows[i].views, item.views)
            self.assertEqual(chapter_rows[i].visitors, item.visitors)

    def test_user_favs(self):
        """ Want list of users on author favs page """
        scraper = FanfictionScraper()
        content = self.users_text.encode("utf-8")
        users_tree = html.fromstring(content)
        users = scraper.get_users(users_tree)
        self.assertEqual(len(users), 186)
        self.assertEqual(users[0].alias, 'abfiaj')
        self.assertEqual(users[0].id, 534893)

    def test_get_chapter_single(self):
        """Want the chapter ids of a particular story """

        scraper = FanfictionScraper()
        content = self.single_text.encode("utf-8")
        single_tree = html.fromstring(content)
        by_country = scraper.get_chapter_single(single_tree)
        self.assertEqual(len(by_country), len(self.ch1_by_country))
        for i, item in enumerate(self.ch1_by_country):
            self.assertEqual(by_country[i].cat, item.cat)
            self.assertEqual(by_country[i].views, item.views)
            self.assertEqual(by_country[i].visitors, item.visitors)


if __name__ == '__main__':
    unittest.main()
