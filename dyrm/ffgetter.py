#!/usr/bin/env python

"""
Page getter for Fanfiction.net
"""
import re
import datetime
from collections import namedtuple
import threading
from lxml import html, etree
from lxml.etree import tostring
import requests
import traceback
import logging
from dyrm.eprint import eprint

# Separate page getter from information scraper.
# Law of Demeter, and easier mocking when we just want to
# test the scraping ability.


def sleeper():
    """ Sleep to space out requests to the site. """
    pass


class PageGetter:
    """ Encapsulate a http page getter with a built-in delay """

    # pylint: disable=too-many-instance-attributes

    # Sleeping thread
    old_sleeper = None

    def __init__(self, session=None, cookie_jar=None, delay=8.0, timeout=18.0):
        if session is None:
            self.session = requests.Session()
            self.is_own_session = True
        else:
            self.session = session
            self.is_own_session = False
        if cookie_jar is None:
            cookie_jar = {}
        self.cjar = cookie_jar
        self.delay = delay
        self.timeout = timeout
        self.response = None

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop_sleep()
        if self.session and self.is_own_session:
            self.session.close()
            self.session = None

    def stop_sleep(self):
        """ Cancel out next sleep so we don't wait at the end """
        try:
            self.old_sleeper.cancel()
        except AttributeError:
            logger = logging.getLogger(__name__)
            logger.debug("sleeper was null")

    def get_page(self, page, payload=None):
        """ Get a page from the fanfiction site """
        if payload is None:
            payload = {}

        # Make sure we have waited long enough before going for a new page.
        active_count = threading.active_count();
        if active_count > 1 and self.old_sleeper is not None:
            self.old_sleeper.join()
            self.old_sleeper = None

        # Start a sleeper so we can delay our access to the
        # next page. Need to wait about 7 seconds to obey the rules.
        self.old_sleeper = threading.Timer(self.delay, sleeper)
        self.old_sleeper.start()

        # Try to make connections less noisy here.
        logging.getLogger(
            'urllib3.connectionpool').setLevel(logging.ERROR)

        try:
            self.response = self.session.get(
                page,
                timeout=self.timeout,
                cookies=self.cjar,
                params=payload)
        except requests.exceptions.Timeout as exc:
            eprint("Page:", page, "Payload:", payload)
            eprint("Timeout problem", exc)
            raise ConnectionAbortedError('Timeout')
        except Exception:
            logger = logging.getLogger(__name__)
            logger.error(traceback.format_exc())
            raise ConnectionAbortedError('Catch-all')

        if self.response.status_code != requests.codes.ok:
            raise ConnectionRefusedError(self.response)

        # Check for logged out page.
        if 'You must be logged in' in self.response.text:
            raise ConnectionRefusedError('Not logged in')

        return html.fromstring(self.response.content)


class FanfictionGetter:
    """ Encapsulate a connection to fanfiction.net """

    def __init__(self, pgetter):
        self.pgetter = pgetter

    def get_old_story_eyes_tree(self, month, year):
        """
            Load the old story eyes tree (monthly story info),
            which also works for individual stories and chapters.
        """
        page = 'https://www.fanfiction.net/stats/story_eyes.php'
        payload = {'month': month, 'year': year}
        old_story_eyes_tree = self.pgetter.get_page(page, payload)
        return old_story_eyes_tree

    def get_story_eyes_tree(self, payload=None):
        """
            Load the story eyes tree (monthly story info),
            which also works for individual stories and chapters.
        """
        page = 'https://www.fanfiction.net/stats/story_eyes.php'
        story_eyes_tree = self.pgetter.get_page(page, payload)
        return story_eyes_tree

    def get_legacy_tree(self):
        """ Get the legacy story page """
        page = 'https://www.fanfiction.net/stats/story.php'
        payload = {}
        legacy_tree = self.pgetter.get_page(page, payload)
        return legacy_tree

    def get_legacy_part(self, ref, part):
        """ Get the legacy part stats (fav or follow) page for a story """
        page = 'https://www.fanfiction.net/stats/part.php'
        payload = {'storyid': ref, 'part': part}
        return self.pgetter.get_page(page, payload)

    def get_comment_tree(self, ref):
        """ Get opening comments page for a story """
        page = 'https://www.fanfiction.net/' + ref
        return self.pgetter.get_page(page)

    def get_chapters_tree(self, ref, payload=None):
        """
            Get chapters for one story. Payload can specify the date.
        """
        page = 'https://www.fanfiction.net/stats/story_eyes_story.php'
        if payload is None:
            payload = {'storyid': ref}
        else:
            payload['storyid'] = ref
        chapters_tree = self.pgetter.get_page(page, payload)
        return chapters_tree

    def get_chapter_single(self, ch_ref, month=None, year=None):
        """ Get a single chapter page """

        page = 'https://www.fanfiction.net/stats/story_eyes_chapter.php'
        payload = {
            'storytextid': ch_ref}
        if month:
            payload['month'] = month
        if year:
            payload['year'] = year
        tree = self.pgetter.get_page(page, payload)
        return tree

    def get_favme(self):
        """ Get user favs page """

        page = 'https://www.fanfiction.net/stats/user.php'
        payload = {'action': 'favs'}
        tree = self.pgetter.get_page(page, payload)
        return tree

    def get_followme(self):
        """ Get user alerts page """

        page = 'https://www.fanfiction.net/stats/user.php'
        payload = {'action': 'alerts'}
        tree = self.pgetter.get_page(page, payload)
        return tree

    def get_user_profile_tree(self, code):
        """ Get the user profile page """
        page = "https://www.fanfiction.net/u/" + str(code)
        tree = self.pgetter.get_page(page)
        return tree

    def get_user_country(self, code):
        """ Get country for user """
        tree = self.get_user_profile_tree(code)
        scraper = FanfictionScraper()
        country = scraper.get_user_country(tree)
        return country

    def get_response(self):
        """ Get response from last page get """
        return self.pgetter.response


class FanfictionScraper:
    """ Encapsulate scraping of data from fanfiction.net """

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.month_story_rows_parser = MonthStoryRowsParser()
        self.month_chapter_rows_parser = MonthChapterRowsParser()
        self.month_caption_parser = MonthCaptionParser()
        self.month_menu_parser = MonthMenuParser()
        self.legacy_parser = LegacyTableParser()
        self.visitor_parser = VisitorChartParser()
        self.user_parser = UserParser()
        self.user_prof_parser = UserProfParser()
        self.user_comment_parser = UserCommentParser()

    def get_month_story_rows(self, eyes_tree):
        """ Get rows for all stories from the monthly story table """

        self.month_story_rows_parser.set_tree(eyes_tree)
        month_story_rows = \
            self.month_story_rows_parser.get_rows()
        return month_story_rows

    def get_titles(self, eyes_tree):
        """ Get titles of all stories from the monthly story table """
        month_story_rows = self.get_month_story_rows(eyes_tree)
        return [
            TitleRec(ref=x.ref, title=x.title)
            for x in month_story_rows]

    def get_titles_dict(self, eyes_tree):
        """ Get dictionary of titles of all stories
            from the monthly story table """
        month_story_rows = self.get_month_story_rows(eyes_tree)
        return dict(
            (x.ref, TitleRec(ref=x.ref, title=x.title))
            for x in month_story_rows)

    def get_month_menu(self, eyes_tree):
        """ Get menu of months """
        self.month_menu_parser.set_tree(eyes_tree)
        return self.month_menu_parser.get_menu()

    def get_month_latest(self, eyes_tree):
        """ Get latest month on menu """
        self.month_menu_parser.set_tree(eyes_tree)
        return self.month_menu_parser.get_month_latest()

    def get_month_caption(self, eyes_tree):
        """ Get caption of monthly page """
        self.month_caption_parser.set_tree(eyes_tree)
        month_caption = self.month_caption_parser.get_caption()
        return month_caption

    def get_month_year(self, eyes_tree):
        """ Get month and year of monthly page """
        month_caption = self.get_month_caption(eyes_tree)
        return month_caption.month, month_caption.year

    def get_comments(self, comment_tree):
        """ Get comment rows from page """
        self.user_comment_parser.set_tree(comment_tree)
        return self.user_comment_parser.get_comments()

    def get_legacy(self, legacy_tree):
        """ Get rows of legacy table """
        self.legacy_parser.set_tree(legacy_tree)
        return self.legacy_parser.get_rows()

    def get_legacy_titles(self, legacy_tree):
        """ Get title records from legacy table """
        self.legacy_parser.set_tree(legacy_tree)
        return self.legacy_parser.get_titles()

    def get_legacy_part(self, part_tree):
        """ Get rows of favs or follows, with user codes """
        self.user_parser.set_tree(part_tree)
        return self.user_parser.get_users()

    def get_monthly_visits(self, eyes_tree):
        """ Get number of montly visits """
        self.visitor_parser.set_tree(eyes_tree)
        by_date = self.visitor_parser.get_visits(0)
        by_country = self.visitor_parser.get_visits(1)
        return by_date, by_country

    def get_chapters_mcap(self, chap_tree):
        """ Get month caption for chapters of one story """

        # The result here will be the caption field.
        self.month_caption_parser.set_tree(chap_tree)
        return self.month_caption_parser.get_caption()

    def get_chapters_visits(self, chap_tree):
        """ Get visitors for chapters of one story """

        # The tables here will be visits for the chapter
        self.visitor_parser.set_tree(chap_tree)
        by_date = self.visitor_parser.get_visits(0)
        by_country = self.visitor_parser.get_visits(1)
        return by_date, by_country

    def get_chapters_rows(self, chap_tree):
        """ Get table rows for chapters of one story """

        # The table here will be by chapter
        mparse2 = self.month_chapter_rows_parser
        mparse2.set_tree(chap_tree)
        return mparse2.get_rows()

    def get_chapter_single(self, single_tree):
        """ Get visitor tables for a single chapter """

        # This will give us one chart by country. By date isn't interesting.
        self.visitor_parser.set_tree(single_tree)
        by_country = self.visitor_parser.get_visits(1)
        return by_country

    def get_users(self, user_tree):
        """ Get the user names and ids from a table of favs or follows """

        self.user_parser.set_tree(user_tree)
        return self.user_parser.get_users()

    def get_user_country(self, user_ptree):
        """ Get the country from the flag on the user page, if any """
        self.user_prof_parser.set_tree(user_ptree)
        return self.user_prof_parser.get_country()


def uncomma(num_str):
    """
    Remove commas and (later) fix other conversion issues
    for numbers from fanfiction.net pages.
    """
    num_str2 = num_str.strip()
    if num_str2 == '':
        return 0
    return int(re.sub(',', '', num_str2))


LegacyRec = namedtuple(
    'LegacyRec',
    ['ref', 'title', 'words', 'chaps', 'reviews',
     'views', 'c2s', 'favs', 'alerts'])


class LegacyTableParser:
    """ Extract information from the legacy story table """

    # Patterns used by the class.
    find_legacy_rows = etree.XPath(
        "//table[@id = 'gui_table1i']/tbody/tr")
    storyid_pattern = re.compile(r"""
        storyid=
        ([0-9]+)
        """, re.VERBOSE)

    def __init__(self):
        self.rows = []

    def set_tree(self, tree):
        """ XPath extract chart scripts """
        self.rows = self.find_legacy_rows(tree)

    def get_num_rows(self):
        """ Number of rows found"""
        return len(self.rows)

    def get_titles(self):
        return [
            TitleRec(ref=x.ref, title=x.title) for x in self.get_rows()]

    def get_rows(self):
        """ Get a record from the table row """
        recs = []
        for row in self.rows:
            href1 = row[0][0].get("href")
            href = 0
            match = re.search(self.storyid_pattern, href1)
            if match:
                href = int(match.group(1))
            rec = LegacyRec(
                ref=href,
                title=row[0].text_content().strip(),
                words=uncomma(row[1].text_content()),
                chaps=uncomma(row[2].text_content()),
                reviews=uncomma(row[3].text_content()),
                views=uncomma(row[4].text_content()),
                c2s=uncomma(row[5].text_content()),
                favs=uncomma(row[6].text_content()),
                alerts=uncomma(row[7].text_content()))
            recs.append(rec)
        return recs


VisCounter = namedtuple('VisCounter', ['cat', 'views', 'visitors'])


class VisitorChartParser:
    """ Extracts information from visitor charts in fanfiction.net """

    # Patterns used by the class
    find_charts = etree.XPath("//script[contains(text(),'new FusionChart')]")
    xml_pattern = re.compile(
        r"""
        setDataXML
        \(\"
        (.*)   # xml contents
        \"\);
        """, re.VERBOSE)

    def __init__(self):
        self.charts = []

    def set_tree(self, tree):
        """ XPath extract chart scripts """
        self.charts = self.find_charts(tree)

    def get_num_charts(self):
        """ Number of charts found"""
        return len(self.charts)

    def get_visits(self, num):
        """
        Extract categories, views, and visitor counts from
        script embedded xml
        """
        if num >= len(self.charts):
            return []

        script = self.charts[num]
        cats = []
        views = []
        visitors = []
        match = re.search(self.xml_pattern, script.text_content())
        if match:
            chart_xml = match.group(1)
            chart_tree = etree.fromstring(chart_xml.replace('\\', ''))
            cats = [item.get("label") for item in chart_tree[0]]
            views = [uncomma(item.get("value")) for item in chart_tree[1]]
            visitors = [uncomma(item.get("value")) for item in chart_tree[2]]
        return [VisCounter(*item) for item in zip(cats, views, visitors)]


MonthMenuRec = namedtuple(
    'MonthMenuRec',
    ['month', 'year'])


class MonthMenuParser:
    """ Extracts the month menu contents from the story eyes page """

    # Patterns used by the class
    find_month_menu = etree.XPath('//select[@name = "date"]/option')
    month_pattern = re.compile(r"""
        ([0-9]+) / ([0-9]+)
        """, re.VERBOSE)

    def __init__(self):
        self.menu_entries = []

    def set_tree(self, tree):
        """ Use XPath to find menu entries """
        self.menu_entries = self.find_month_menu(tree)

    def get_menu(self):
        """ Get entire month menu contents """
        recs = []
        for entry in self.menu_entries:
            recs.append(entry.text_content())
        return recs

    def get_month_latest(self):
        """ Get last month and year available in month menu """
        rec = self.menu_entries[0].text_content()
        m_match = re.search(self.month_pattern, rec)
        if m_match:
            month = m_match.group(1)
            year = m_match.group(2)
            return MonthMenuRec(month=month, year=year)
        return None

TitleRec = namedtuple(
    'TitleRec',
    ['ref', 'title'])


MonthlyStoryRec = namedtuple(
    'MonthlyStoryRec',
    ['ref', 'title', 'words', 'views', 'visitors'])


class MonthStoryRowsParser:
    """ Extracts information from monthly story table in fanfiction.net """

    # Patterns used by the class
    find_story_table = etree.XPath('//table[@id = "gui_table2i"]/tbody/tr')
    find_story_href = etree.XPath('//table[@id = "gui_table2i"]/tbody/tr/td/a')
    storyid_pattern = re.compile(r"""
        storyid=
        ([0-9]+)
        """, re.VERBOSE)

    def __init__(self):
        self.story_rows = []
        self.story_href = []

    def set_tree(self, tree):
        """ Use XPath to find monthly story rows """
        self.story_rows = self.find_story_table(tree)
        self.story_href = self.find_story_href(tree)

    def ref_from_href(self, href):
        """ extract the chapter id number from the href string """
        ref = 0
        s_match = re.search(self.storyid_pattern, href.attrib['href'])
        if s_match:
            ref = int(s_match.group(1))
        return ref

    def get_rows(self):
        """ Turn table text into records,
            adding in the storyids from the hrefs
        """
        if len(self.story_rows) != len(self.story_href):
            eprint("Mismatch in story rows and refs")
            return False
        combined = zip(self.story_rows, self.story_href)

        recs = []
        for row, href in combined:
            cols = row.text_content().split("\n")
            sref = self.ref_from_href(href)
            recs.append(
                MonthlyStoryRec(
                    ref=sref,
                    title=cols[1].strip(),
                    words=uncomma(cols[2]),
                    views=uncomma(cols[3]),
                    visitors=uncomma(cols[4])))
        return recs


MonthCaption = namedtuple(
    'MonthCaption',
    ['year', 'month', 'views', 'visitors'])


class MonthCaptionParser:
    """ Extracts information from month caption in fanfiction.net """

    # Patterns used by the class
    find_month_captions = etree.XPath(
        "//table[@id = 'gui_table1i']/" +
        "tbody/tr/td[text()[contains(.,'month')]]")
    m_pattern = re.compile(r"""
        For\ the\ month\ of\s
        (\d+)  # year
        -
        (\d+)   # month
        \,\ there\ have\ been\ a\ total\ of\s+
        ([0-9,]+)
        \ Views\ and\s
        ([0-9,]+)
        \ Visitors
        """, re.VERBOSE)

    def __init__(self):
        self.month_captions = None

    def set_tree(self, tree):
        """ Use XPath to find month caption fields"""
        self.month_captions = self.find_month_captions(tree)

    def get_caption(self):
        """
        Get information about the date, and the monthly totals
        from the story_eyes content.
        """
        for td_item in self.month_captions:
            text = td_item.text_content()
            m_match = re.search(self.m_pattern, text)
            if m_match:
                (year, month, views, visitors) = \
                    m_match.group(1, 2, 3, 4)
                return MonthCaption(
                    year, month, uncomma(views), uncomma(visitors))
        return None


UserRec = namedtuple(
    'UserRec',
    ['id', 'alias', 'date_added'])


class UserParser:
    """ Extract user information from a table of favorites or follows """

    # Patterns used by the class
    find_user_table = etree.XPath('//table[@id = "gui_table1i"]/tbody/tr')
    find_user_href = \
        etree.XPath('//table[@id = "gui_table1i"]/tbody/tr/td/a')
    userid_pattern = re.compile(r"""
        /u/
        ([0-9]+)
        /
        """, re.VERBOSE)

    def __init__(self):
        self.user_rows = []
        self.user_href = []

    def set_tree(self, tree):
        """ Use XPath to find user rows """
        self.user_rows = self.find_user_table(tree)
        self.user_href = self.find_user_href(tree)

    def ref_from_href(self, href):
        """ extract the chapter id number from the href string """
        ref = 0
        s_match = re.search(self.userid_pattern, href.attrib['href'])
        if s_match:
            ref = int(s_match.group(1))
        return ref

    def get_users(self):
        """ Turn table text into user records """
        if len(self.user_rows) != len(self.user_href):
            eprint("Mismatch in user rows and refs")
            return False
        combined = zip(self.user_rows, self.user_href)

        recs = []
        for row, href in combined:
            ref = self.ref_from_href(href)
            cols = row.text_content().split("\n")
            new_rec = UserRec(
                id=ref,
                alias=cols[1].strip(),
                date_added=cols[2].strip())
            recs.append(new_rec)
        return recs


class UserCommentParser:
    """ Extract information from a comment page """

    # patterns used in the class
    chapter_pattern = re.compile(r"""
        chapter
        \s+
        ([0-9]+)
        """, re.VERBOSE)
    ref_pattern = re.compile(r"""
        ([0-9]+)
        """, re.VERBOSE)
    find_comments_raw = etree.XPath(
        '//td[@style = "padding-top:10px;padding-bottom:10px"]')
    find_comments_chapter = etree.XPath(
        '//td[@style = "padding-top:10px;padding-bottom:10px"]' +
        '/small[@style = "color:gray"]')
    find_comments_date = etree.XPath(
        '//td[@style = "padding-top:10px;padding-bottom:10px"]' +
        '/small/*[@data-xutime]')
    find_comments_text = etree.XPath(
        '//td[@style = "padding-top:10px;padding-bottom:10px"]' +
        '/div[@style = "margin-top:5px"]')
    find_next = etree.XPath("//a[contains(text(),'Next ')]")

    def __init__(self):
        self.raw_comments = []
        self.chapter_comments = []
        self.date_comments = []
        self.date_text = []

    def set_tree(self, tree):
        self.next = self.find_next(tree)
        self.raw_comments = self.find_comments_raw(tree)
        self.chapter_comments = self.find_comments_chapter(tree)
        self.date_comments = self.find_comments_date(tree)
        self.date_text = self.find_comments_text(tree)

    def get_comments(self):
        # Item may be signed or not. If so, it has an href to the user.
        # Otherwise, there is only a name string.
        signers = []
        if not self.raw_comments:
            return None, [], [], [], []
        if self.raw_comments[0].text_content() == 'No Reviews found.':
            return None, [], [], [], []
        for raw in self.raw_comments:
            a_element = raw.find('a')
            if a_element is not None:
                myref = a_element.attrib['href']
                refnum = 0
                match = re.search(self.ref_pattern, myref)
                if match:
                    refnum = int(match.group(1))
                mytext = a_element.text_content()
                signers.append((refnum, mytext))
            else:
                myname = tostring(raw[1])
                mypos = myname.index(b'>') + 2
                myname_end = myname[mypos:-1].decode('utf-8')
                signers.append((0, myname_end))
        chapters = []
        for chapter in self.chapter_comments:
            chap = 1
            match = re.search(self.chapter_pattern, chapter.text_content())
            if match:
                chap = int(match.group(1))
            chapters.append(chap)
        dates = [
            datetime.datetime.fromtimestamp(
                int(x.attrib['data-xutime'])) for x in self.date_comments]
        text_comments = [x.text_content() for x in self.date_text]
        mynext = None
        if self.next:
            mynext = self.next[0].attrib['href']
        return mynext, dates, chapters, text_comments, signers


class UserProfParser:
    """ Extract information from a user profile page """

    # patterns used in the class
    find_country = etree.XPath("//table//img[@align='ABSMIDDLE']")

    def __init__(self):
        self.user_flag = None

    def set_tree(self, tree):
        """ Use XPath to find month caption fields"""
        self.user_flag = self.find_country(tree)

    def get_country(self):
        """ get the country from the flag label, if any """
        if len(self.user_flag) > 0:
            country = self.user_flag[0].get("title", "")
        else:
            country = ""
        return country


MonthlyChapterRec = namedtuple(
    'MonthlyChapterRec',
    ['ch_ref', 'num', 'title', 'words', 'views', 'visitors'])


class MonthChapterRowsParser:
    """ Extracts information from monthly chapter table
        (for one story) in fanfiction.net
    """

    # Patterns used by the class
    find_chapter_table = etree.XPath('//table[@id = "gui_table2i"]/tbody/tr')
    find_chapter_href = \
        etree.XPath('//table[@id = "gui_table2i"]/tbody/tr/td/a')
    textid_pattern = re.compile(r"""
        storytextid=
        ([0-9]+)
        """, re.VERBOSE)

    def __init__(self):
        self.chapter_rows = []
        self.chapter_href = []

    def set_tree(self, tree):
        """ Use XPath to find monthly chapter rows """
        self.chapter_rows = self.find_chapter_table(tree)
        self.chapter_href = self.find_chapter_href(tree)

    def ref_from_href(self, href):
        """ extract the chapter id number from the href string """
        ref = 0
        s_match = re.search(self.textid_pattern, href.attrib['href'])
        if s_match:
            ref = int(s_match.group(1))
        return ref

    def get_rows(self):
        """ Turn table text into records,
            adding in the chapterids from the hrefs
        """
        if len(self.chapter_rows) != len(self.chapter_href):
            eprint("Mismatch in chapter rows and refs")
            return False
        combined = zip(self.chapter_rows, self.chapter_href)

        recs = []
        for row, href in combined:
            ref = self.ref_from_href(href)
            cols = row.text_content().split("\n")
            new_rec = MonthlyChapterRec(
                ch_ref=ref,
                num=uncomma(cols[1]),
                title=cols[2].strip(),
                words=uncomma(cols[3]),
                views=uncomma(cols[4]),
                visitors=uncomma(cols[5]))
            recs.append(new_rec)
        return recs


def main():
    """ Main test driver. Expect to fetch the page without cookies. """
    try:
        logger = logging.getLogger(__name__)
        with requests.Session() as session:
            getter = PageGetter(session)
            getter.get_page('https://www.fanfiction.net')
            logger.info("Got the page")
            getter.stop_sleep()
    except ConnectionRefusedError:
        eprint("Page needs cookies for access")
    except ConnectionAbortedError:
        eprint("Connection problem")


# Test the script, see if we are logged into fanfiction.net
if __name__ == "__main__":
    main()
