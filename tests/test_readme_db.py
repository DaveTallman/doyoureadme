# -*- coding: utf-8 -*-

from context import dyrm

"""Tests for ReadMeDb."""
import os
import unittest
import json
from dyrm.ffgetter import TitleRec, MonthlyChapterRec
from dyrm.readme_db import ReadMeDb


def _safe_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


class ReadMeDbTestCase(unittest.TestCase):
    """ Mocked unit tests, if possible """

    def setUp(self):
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
        self.chapters = [
            MonthlyChapterRec(
                ch_ref=6393657, num=1,
                title="Chapter 1, Bad Beginning",
                words=668, views=12, visitors=12),
            MonthlyChapterRec(
                ch_ref=6398498, num=2,
                title="Chapter 2, Buddy", words=1169,
                views=5, visitors=5),
            MonthlyChapterRec(
                ch_ref=6401855, num=3,
                title="Chapter 3, Box", words=639,
                views=4, visitors=4),
            MonthlyChapterRec(
                ch_ref=6405924, num=4,
                title="Chapter 4, Breaking",
                words=1446, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6412296, num=5,
                title="Chapter 5, Book",
                words=1272, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6417302, num=6,
                title="Chapter 6, Baby",
                words=533, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6422829, num=7,
                title="Chapter 7, Battle",
                words=1685, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6531019, num=8,
                title="Book the 2nd, The RapTile Room",
                words=1239, views=4, visitors=2),
            MonthlyChapterRec(
                ch_ref=6545008, num=9,
                title="Chapter 2, Ringer",
                words=935, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6552293, num=10,
                title="Chapter 3, Riot",
                words=620, views=2, visitors=2),
            MonthlyChapterRec(
                ch_ref=6557175, num=11,
                title="Chapter 4, Return",
                words=1193, views=3, visitors=2),
            MonthlyChapterRec(
                ch_ref=6562410, num=12,
                title="Chapter 1 of Book the 3rd, White Window",
                words=771, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6567767, num=13,
                title="Chapter 2, Window shopping",
                words=1071, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6573214, num=14,
                title="Chapter 3, Wishy Washy",
                words=641, views=0, visitors=0),
            MonthlyChapterRec(
                ch_ref=6576386, num=15,
                title="Chapter 4, War",
                words=1176, views=1, visitors=1)]

    def tearDown(self):
        pass

    def test_last_mtop(self):
        """ Want to know if get_last_mtop works """
        with ReadMeDb() as read_db:
            mtop = read_db.get_last_mtop()
            self.assertTrue(mtop.date.year >= 2016)

    def test_get_last_month(self):
        """ Want to know if get_mtop works """
        with ReadMeDb() as read_db:
            last_month = read_db.get_last_month()
            self.assertTrue(last_month.year >= 2016)

    def test_get_titles_dict(self):
        """ Want to know if Stories titles are good """
        with ReadMeDb() as read_db:
            db_titles = read_db.get_titles_dict()
            self.assertTrue(len(db_titles), len(self.titles))
            for item in self.titles:
                self.assertTrue(db_titles[item.ref])
                self.assertEqual(db_titles[item.ref], item.title)

    def test_get_stories_dict(self):
        """ Get the actual story records """
        with ReadMeDb() as read_db:
            db_stories = read_db.get_stories()
            self.assertTrue(len(db_stories), len(self.titles))

    def test_create_story_table(self):
        """ Want to know if we can create a story table from scratch """
        bogus_db = 'bogus.db'
        _safe_remove(bogus_db)
        with ReadMeDb(bogus_db) as read_db:
            db_titles = read_db.get_titles_dict()
            self.assertFalse(db_titles)
            read_db.batch_insert_stories(self.titles)
            db_titles = read_db.get_titles_dict()
            self.assertTrue(len(db_titles), len(self.titles))
            for item in self.titles:
                self.assertTrue(db_titles[item.ref])
                self.assertEqual(db_titles[item.ref], item.title)
        _safe_remove(bogus_db)

    def test_get_or_create_user(self):
        """
        Want users to be created if they don't exist.
        Try fav and follow once the user is in place.
        """
        with ReadMeDb() as read_db:
            code = 2734390
            country = "Italy"
            new_user = read_db.get_or_create_user(code, country)
            self.assertTrue(new_user.country != country)
            new_favme = read_db.get_or_create_favme(code)
            self.assertEqual(new_favme.code, code)
            new_followme = read_db.get_or_create_followme(code)
            self.assertEqual(new_followme.code, code)

    def test_get_or_create_alias(self):
        """ Want aliases to be created if they don't exist. """
        with ReadMeDb() as read_db:
            code = 2734390
            name = "natalie1668"
            alias = read_db.get_or_create_alias(code, name)
            self.assertEqual(alias.code, code)
            self.assertEqual(alias.name, name)

    def test_get_or_create_story(self):
        """ Want stories to be created if they don't exist. """
        with ReadMeDb() as read_db:
            db_titles = read_db.get_titles_dict()
            ref = 123
            title = "New Story"
            self.assertTrue(ref not in db_titles)
            new_story = read_db.get_or_create_story(ref, title)
            self.assertEqual(new_story.ref, ref)
            self.assertEqual(new_story.title, title)
            db_titles = read_db.get_titles_dict()
            self.assertTrue(ref in db_titles)

    def test_get_fav_counts(self):
        """ Count favorites by story """
        with ReadMeDb() as read_db:
            fav_counts = read_db.get_fav_counts()
            self.assertTrue(len(fav_counts) >= 101)

    def test_get_follow_counts(self):
        """ Count follows by story """
        with ReadMeDb() as read_db:
            follow_counts = read_db.get_follow_counts()
            self.assertTrue(len(follow_counts) >= 84)

    # def test_get_or_create_monthly(self):
    #     """ Want a monthly record created if it doesn't exist """
    #     bogus_db = 'bogus3.db'
    #     _safe_remove(bogus_db)
    #     with ReadMeDb(bogus_db) as read_db:
    #         mrec1 = read_db.get_last_monthly()
    #         self.assertEqual(None, mrec1)
    #         monthly_rec =\
    #             read_db.get_or_create_monthly(month="09", year="2016")
    #         self.assertEqual("2016/09", monthly_rec.date)
    #         rec = json.loads(monthly_rec.json_text)
    #         self.assertTrue("m_visitors" in rec)
    #         self.assertEqual(0, rec["m_visitors"])
    #         self.assertTrue("m_views" in rec)
    #         self.assertEqual(0, rec["m_views"])
    #         self.assertTrue("m_by_country" in rec)
    #         self.assertTrue(not rec["m_by_country"])
    #         self.assertTrue("m_by_date" in rec)
    #         self.assertTrue(not rec["m_by_date"])
    #         self.assertTrue("m_stories" in rec)
    #         self.assertTrue(not rec["m_stories"])

    def test_set_commit(self):
        """ Want to know if we can get a commit """
        bogus_db = 'bogus2.db'
        _safe_remove(bogus_db)
        with ReadMeDb(bogus_db) as read_db:
            read_db.batch_insert_stories(self.titles)
            read_db.set_commit_flag()
        with ReadMeDb(bogus_db) as read_db:
            db_titles = read_db.get_titles_dict()
            self.assertTrue(1256016 in db_titles)
        _safe_remove(bogus_db)


if __name__ == '__main__':
    unittest.main()
