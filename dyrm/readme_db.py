#!/usr/bin/env python

"""
Local database to track story hits and other information for
fanfiction writers.
"""
from collections import namedtuple
from sqlalchemy import create_engine, Column
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy import Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func
from sqlalchemy.engine import Engine
from sqlalchemy import event
import sqlite3


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """ Set foreign keys constraint for sqlite3 """
    # play well with other DB backends
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Like the other case, it would nicer to split into two classes, one
# that sets up an engine and provides a Session, and one that just
# uses a Session, to make mocking easier. We can do both within
# this one package.fav


def legacy_recs_iter(legacy_recs):
    """ turn LegacyRec list into tuples for insertion into Legacy table """
    for rec in legacy_recs:
        yield (
            rec.ref,
            rec.words,
            rec.chaps,
            rec.reviews,
            rec.views,
            rec.c2s,
            rec.favs,
            rec.alerts)


LegacyRecNoTitle = namedtuple(
    'LegacyRecNoTitle',
    ['ref', 'words', 'chaps', 'reviews',
     'views', 'c2s', 'favs', 'alerts'])

Base = declarative_base()

Session = sessionmaker()


class Stories(Base):
    " Represents stories and their titles "

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'stories'

    ref = Column(Integer, primary_key=True)
    title = Column(String)

    legacy = relationship(
        "Legacy", back_populates="story",
        cascade="all, delete, delete-orphan")

    chapters = relationship(
        "Chapters", back_populates="story",
        cascade="all, delete, delete-orphan")

    check_pend = relationship(
        "CheckPend", back_populates="story",
        cascade="all, delete, delete-orphan")

    def __repr__(self):
        return "<Stories(ref=%d, title='%s')>" % (
            self.ref, self.title)


class Comments(Base):
    """ Represents comments on story chapters """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'comments'

    num = Column(Integer, nullable=False, primary_key=True)
    ref = Column(
        Integer, ForeignKey('stories.ref'), nullable=False)
    chapter = Column(Integer, nullable=False)
    name = Column(String)
    comment = Column(String)
    stamp = Column(DateTime)

    signed = relationship("SComments", back_populates="comment")

    def __repr__(self):
        return "<Comments(num= %d, ref=%d, chapter='%d')>" % (
            self.num, self.ref, self.chapter)


class SComments(Base):
    """ Represents comments signed by users """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'scomments'

    num = Column(
        Integer, ForeignKey('comments.num'), nullable=False, primary_key=True)
    code = Column(
        Integer, ForeignKey('users.code'), nullable=False)

    comment = relationship("Comments", back_populates="signed")
    user = relationship("Users")

    def __repr__(self):
        return "<SComments(num= %d, code=%d)>" % (
            self.num, self.code)


class CheckPend(Base):
    """ Represents stories that need chapters checked. """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'checkpend'

    ref = Column(
        Integer, ForeignKey('stories.ref'), nullable=False, primary_key=True)
    check_pending = Column(Integer, default=0)

    story = relationship("Stories")

    def __repr__(self):
        return "<CheckPend(ref=%d, check_pending='%d')>" % (
            self.ref, self.check_pending)


class Ao3Stories(Base):
    """ Represents story records from A03 """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'ao3stories'

    title = Column(String, primary_key=True)
    hits = Column(Integer, default=0)
    kudos = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    bookmarks = Column(Integer, default=0)
    ref = Column(Integer, default=0)

    def __repr__(self):
        return "<A03Stories(title='%s')>" % (
            self.title)


class Favs(Base):
    """ Represents stories favorited by users """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'favs'

    ref = Column(
        Integer, ForeignKey('stories.ref'), nullable=False, primary_key=True)
    code = Column(
        Integer, ForeignKey('users.code'), nullable=False, primary_key=True)
    dt = Column(String)

    user = relationship(
        "Users", back_populates="favorites")

    story = relationship("Stories")

    def __repr__(self):
        return "<Favs(ref=%d, code='%s')>" % (
            self.ref, self.code)


class Follows(Base):
    """ Represents stories followed by users """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'follows'

    ref = Column(
        Integer, ForeignKey('stories.ref'), nullable=False, primary_key=True)
    code = Column(
        Integer, ForeignKey('users.code'), nullable=False, primary_key=True)
    dt = Column(String)

    user = relationship(
        "Users", back_populates="follows")

    story = relationship("Stories")

    def __repr__(self):
        return "<Follows(ref=%d, code='%s')>" % (
            self.ref, self.code)


class Chapters(Base):
    " Represents chapters of stories "

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'chapters'

    # Preserve the most stable part of MonthlyChapterRec =
    # ['ch_ref', 'num', 'title', 'words', 'views', 'visitors']
    ch_ref = Column(Integer, primary_key=True)
    story_ref = Column(Integer, ForeignKey('stories.ref'), nullable=False)
    num = Column(Integer, default=1)
    title = Column(String, default="")
    words = Column(Integer, default=0)
    __table_args__ = (
        Index('story_chapter', "story_ref", "num", unique=True),)

    story = relationship(
        "Stories", back_populates="chapters")

    def __repr__(self):
        pt1 = "<Chapters(ch_ref={0:d}, story_ref={1:d}, ".format(
            self.ch_ref, self.story_ref)
        pt2 = "num={0:d}, title='{1}', words={2:d} )>".format(
            self.num, self.title, self.words)
        return pt1 + pt2


class Users(Base):
    """ Represent readers and writers of stories """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'users'

    code = Column(Integer, primary_key=True)
    country = Column(String, default="")
    date_added = Column(String, default='00-00-0000')

    __table_args__ = (
        Index('user_country', "country", unique=False),)

    favme = relationship(
        "FavMe", back_populates="user")

    followme = relationship(
        "FollowMe", back_populates="user")

    aliases = relationship(
        "Aliases", back_populates="user")

    favorites = relationship(
        "Favs", back_populates="user")

    follows = relationship(
        "Follows", back_populates="user")

    def __repr__(self):
        return "<Users(code={0:d}, country='{1}', date_added='{2}')>".format(
            self.code, self.country, self.date_added)


class Aliases(Base):
    """ Represents aliases of users (can change over time) """

    __tablename__ = 'aliases'

    code = Column(
        Integer, ForeignKey('users.code'), nullable=False, primary_key=True)
    name = Column(String, default="", nullable=False, primary_key=True)
    dt = Column(DateTime, default=func.now())

    user = relationship(
        "Users", back_populates="aliases")

    def __repr__(self):
        return "<Aliases(code={0:d}, name='{1}', dt='{2}')>".format(
            self.code, self.name, self.dt)


class FavMe(Base):
    """ Users who have favorited me """
    __tablename__ = 'favme'

    code = Column(Integer, ForeignKey('users.code'), primary_key=True)
    dt = Column(DateTime, default=func.now())

    user = relationship(
        "Users", back_populates="favme")

    def __repr__(self):
        return "<FaveMe(code={0:d})>".format(self.code)


class FollowMe(Base):
    """ Users who have favorited me """
    __tablename__ = 'followme'

    code = Column(Integer, ForeignKey('users.code'), primary_key=True)
    dt = Column(DateTime, default=func.now())

    user = relationship(
        "Users", back_populates="followme")

    def __repr__(self):
        return "<FollowMe(code={0:d})>".format(self.code)


# class Monthly(Base):
#     """ Represents monthly hit statistics """

#     # pylint: disable=too-few-public-methods,no-init

#     date = Column(String, primary_key=True)
#     json_text = Column(String, default="")

#     __tablename__ = 'monthly'

#     def get_month_year(self):
#         """ Split out month and year from date """
#         parts = self.date.split("/")
#         return parts[1], parts[0]

#     def __repr__(self):
#         return "<Monthly(date=%s)>" % (self.date)


class Months(Base):
    """ Represents months we have on record """

    # pylint: disable=too-few-public-methods,no-init

    mid = Column(Integer, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)

    __tablename__ = 'months'

    def __repr__(self):
        return "<Months(mid={0:d}, year={1:d}, month={2:d})>".format(
            self.mid, self.year, self.month)


class MTop(Base):
    """ Top of the month views summary """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mtop'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    day = Column(Integer, default=0)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")

    def __repr__(self):
        str = "<MTop(mid={0:d}, day={1:d}, views={2:d}, visitors={3:d})>"
        return str.format(
            self.mid, self.day, self.views, self.visitors)


class MStory(Base):
    """ Monthly visitors and views by story """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mstory'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    ref = Column(Integer, ForeignKey('stories.ref'), primary_key=True)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")
    story = relationship("Stories")

    def __repr__(self):
        str = "<MStory(mid={0:d}, ref={1:d}, views={2:d}, visitors={3:d})>"
        return str.format(
            self.mid, self.ref, self.views, self.visitors)


class MCtry(Base):
    """ Monthly visitors and views by story """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mctry'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    country = Column(String, primary_key=True)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")

    def __repr__(self):
        str = "<MCtry(mid={0:d}, country={1}, views={2:d}, visitors={3:d}>"
        return str.format(
            self.mid, self.country, self.views, self.visitors)


class MStoryCtry(Base):
    """ Monthly visitors and views by story """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mstoryctry'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    ref = Column(Integer, ForeignKey('stories.ref'), primary_key=True)
    country = Column(String, primary_key=True)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")
    story = relationship("Stories")

    def __repr__(self):
        str = "<MStoryCtry(mid={0:d}, ref={1:d}, country={2}>"
        return str.format(
            self.mid, self.ref, self.country)


class MChap(Base):
    """ Monthly visitors and views by story """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mchap'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    ref = Column(Integer, ForeignKey('stories.ref'), primary_key=True)
    chap = Column(Integer, primary_key=True)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")
    story = relationship("Stories")

    def __repr__(self):
        str = "<MChap(mid={0:d}, ref={1:d}, chap={2:d}, views={3:d}, visitors={4:d})>"
        return str.format(
            self.mid, self.ref, self.chap, self.views, self.visitors)


class MChapCtry(Base):
    """ Monthly visitors and views by story """

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'mchapctry'

    mid = Column(Integer, ForeignKey('months.mid'), primary_key=True)
    ref = Column(Integer, ForeignKey('stories.ref'), primary_key=True)
    chap = Column(Integer, primary_key=True)
    country = Column(String, primary_key=True)
    views = Column(Integer, default=0)
    visitors = Column(Integer, default=0)

    date = relationship("Months")
    story = relationship("Stories")

    def __repr__(self):
        str = "<MChapCtry(mid={0:d}, ref={1:d}, chap={2:d}, country={3:d})>"
        return str.format(
            self.mid, self.ref, self.chap, self.country)


class Legacy(Base):
    " Legacy story hit information "

    # pylint: disable=too-few-public-methods,no-init

    __tablename__ = 'legacy'

    ref = Column(Integer, ForeignKey('stories.ref'), primary_key=True)
    chaps = Column(Integer, default=1)
    reviews = Column(Integer, default=0)
    views = Column(Integer, default=0)
    c2s = Column(Integer, default=0)
    favs = Column(Integer, default=0)
    alerts = Column(Integer, default=0)

    story = relationship("Stories", back_populates="legacy")

    def __repr__(self):
        recstr = \
            "<Legacy(ref=%d, chaps='%s', reviews=%d, views=%d, "\
            + "c2s=%d, favs=%d, alerts=%d)>"
        return recstr % (
            self.ref, self.chaps, self.reviews,
            self.views, self.c2s, self.favs, self.alerts)


def legacy_query_to_dict_iter(recs):
    """ turn Legacy table query into dictionary lookup """
    for rec in recs:
        yield rec[0], LegacyRecNoTitle(*rec)


def format_date(month, year):
    """ String format for key """
    return "{}/{}".format(year, month)


class ReadMeDb:
    """ Database to store hit levels to compare with new ones """

    def __init__(self, file="dbs/readme.db", echo=False):
        self.sql_file = file
        engine_str = "sqlite:///{0}".format(self.sql_file)
        self.engine = create_engine(engine_str, echo=echo)
        self.titles = {}
        self.legacy = {}
        Base.metadata.create_all(self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()
        self.commit_flag = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.commit_flag:
            self.session.commit()
        self.session.close()

    def set_commit_flag(self, flag=True):
        """ Tell the db to commit (or not) when it closes """
        self.commit_flag = flag

    def get_stories(self):
        """ Get all stories """
        return self.session.query(Stories).all()

    def set_check_pending(self, ref):
        """ Set a chapter check pending for a story """
        pending = self.session.query(
            CheckPend).filter_by(ref=ref).first()
        if pending:
            pending.check_pending = 1
            return
        pending = CheckPend(ref=ref, check_pending=1)
        self.session.add(pending)

    def get_checks_pending(self):
        """ Get the list of stories that need chapter checking """
        pending = self.session.query(
            CheckPend).filter_by(check_pending=1).all()
        new_pending = [
            (item.ref, item.story.title) for item in pending]
        return sorted(new_pending, key=lambda tup: tup[1])

    def clear_checks_pending(self):
        """" CLear the list of stories that need chapter checking """
        pending = self.session.query(
            CheckPend).filter_by(check_pending=1).all()
        for item in pending:
            item.check_pending = 0

    def get_fav_counts(self):
        """ Get story favorites counts """
        fav_counts = self.session.query(
            Favs.ref, func.count(Favs.ref)).group_by(Favs.ref).all()
        return fav_counts

    def get_favs_for_story(self, ref):
        """ Get story favorite records """
        fav_recs = self.session.query(Favs).filter_by(ref=ref).all()
        return fav_recs

    def get_follows_for_story(self, ref):
        """ Get story follow records """
        follow_recs = self.session.query(Follows).filter_by(ref=ref).all()
        return follow_recs

    def get_favs_for_me(self):
        """ Get user favorite records """
        fav_recs = self.session.query(FavMe).all()
        return fav_recs

    def get_follows_for_me(self):
        """ Get user follow records """
        follow_recs = self.session.query(FollowMe).all()
        return follow_recs

    def get_follow_counts(self):
        """ Get story follows counts """
        follow_counts = self.session.query(
            Follows.ref, func.count(Follows.ref)).group_by(Follows.ref).all()
        return follow_counts

    def get_titles_dict(self):
        """ Get the titles from the Stories table as a dictionary """
        self.titles = {}
        for ref, title in self.session.query(Stories.ref, Stories.title):
            self.titles[ref] = title
        return self.titles

    def find_users_with_country(self, country):
        """ Get users that have a given country name """
        user_recs = self.session.query(Users).filter_by(country=country).all()
        return user_recs

    def find_users_with_code(self, code):
        """ Get users that have a given country name """
        user_recs = self.session.query(Users).filter_by(code=code).all()
        return user_recs

    def batch_insert_ao3_stories(self, stories):
        """ Insert many new ao3 stories at once """
        new_stories = [
            Ao3Stories(
                title=item["title"], hits=item["hits"], kudos=item["kudos"],
                comments=item["comments"],
                bookmarks=item["bookmarks"]) for item in stories]
        self.session.bulk_save_objects(new_stories)

    def batch_insert_stories(self, stories):
        """ Insert many new stories at once """
        new_stories = [
            Stories(ref=item.ref, title=item.title) for item in stories]
        self.session.bulk_save_objects(new_stories)

    def get_or_create_user(self, code, country):
        """ Add to the Users data table if not there """
        user = self.session.query(Users).filter_by(code=code).first()
        if user:
            return user
        user = Users(code=code, country=country)
        self.session.add(user)
        return user

    def get_or_create_favme(self, code):
        """ Add to the Users data table if not there """
        favme = self.session.query(FavMe).filter_by(code=code).first()
        if favme:
            return favme
        favme = FavMe(code=code)
        self.session.add(favme)
        return favme

    def get_or_create_followme(self, code):
        """ Add to the Users data table if not there """
        followme = self.session.query(FollowMe).filter_by(code=code).first()
        if followme:
            return followme
        followme = FollowMe(code=code)
        self.session.add(followme)
        return followme

    def get_or_create_alias(self, code, name):
        """ Add to the Aliases data table if not there """
        alias = self.session.query(
            Aliases).filter_by(code=code, name=name).first()
        if alias:
            return alias
        alias = Aliases(code=code, name=name)
        self.session.add(alias)
        return alias

    def get_or_create_story(self, ref, title):
        """ Add to the Stories data table if not there """
        story = self.session.query(Stories).filter_by(ref=ref).first()
        if story:
            return story
        story = Stories(ref=ref, title=title)
        self.session.add(story)
        return story

    def get_or_create_ao3_story(self, title):
        """ Add to the Stories data table if not there """
        story = self.session.query(Ao3Stories).filter_by(title=title).first()
        if story:
            return story
        story = Ao3Stories(title=title)
        self.session.add(story)
        return story

    def get_last_month(self):
        """ Get latest month record """
        last_month = self.session.query(
            Months).order_by(Months.year.desc(), Months.month.desc()).first()
        return last_month

    def get_last_mid(self):
        """ Get last month id """
        last_month = self.get_last_month()
        if not last_month:
            return 0
        return last_month.mid

    def get_last_mtop(self):
        """ Get top monthly summary record """
        last_month = self.get_last_month()
        last_mtop = self.session.query(
            MTop).filter_by(mid=last_month.mid).first()
        return last_mtop

    def get_last_monthly(self):
        """ Get last month saved in DB """
        last_monthly = self.session.query(
            Monthly).order_by(Monthly.date.desc()).first()
        return last_monthly

    def get_or_create_mtop(self, mid):
        """ Find or create the monthly top record. """
        rec = self.session.query(
            MTop).filter_by(mid=mid).first()
        if rec:
            return rec
        rec = MTop(mid=mid, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_mctry(self, mid, country):
        """ Find or create the monthly country top record. """
        rec = self.session.query(
            MCtry).filter_by(mid=mid, country=country).first()
        if rec:
            return rec
        rec = MCtry(mid=mid, country=country, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_mstory(self, mid, ref):
        """ Find or create the montly story country record. """
        rec = self.session.query(
            MStory).filter_by(mid=mid, ref=ref).first()
        if rec:
            return rec
        rec = MStory(mid=mid, ref=ref, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_mchap(self, mid, ref, chap):
        """ Find or create the monthly story chapter record. """
        rec = self.session.query(
            MChap).filter_by(mid=mid, ref=ref, chap=chap).first()
        if rec:
            return rec
        rec = MChap(mid=mid, ref=ref, chap=chap, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_mstoryctry(self, mid, ref, country):
        """ Find or create the monthly story country record. """
        rec = self.session.query(
            MStoryCtry).filter_by(mid=mid, ref=ref, country=country).first()
        if rec:
            return rec
        rec = MStoryCtry(
            mid=mid, ref=ref, country=country, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_chapctry(self, mid, ref, chap, country):
        """ Find or create the monthly story country record. """
        rec = self.session.query(
            MChapCtry).filter_by(
            mid=mid, ref=ref, chap=chap, country=country).first()
        if rec:
            return rec
        rec = MChapCtry(
            mid=mid, ref=ref, chap=chap, country=country, views=0, visitors=0)
        self.session.add(rec)
        return rec

    def get_or_create_month(self, month, year, mid):
        """ Find or create a month record """
        rec = self.session.query(
            Months).filter_by(month=month, year=year).first()
        if rec:
            return rec
        rec = Months(month=month, year=year, mid=mid)
        self.session.add(rec)
        return rec

    def get_or_create_chapter(self, sref, rec):
        """ Add to the Chapters data table if not there """
        chapter = \
            self.session.query(Chapters).filter_by(ch_ref=rec.ch_ref).first()
        if chapter:
            return chapter
        chapter = Chapters(
            ch_ref=rec.ch_ref, story_ref=sref, num=rec.num,
            title=rec.title, words=rec.words)
        self.session.add(chapter)
        return chapter

    def create_empty_legacy(self, new_ref):
        " Make a new empty rec for given legacy key"
        new_legacy = Legacy(ref=new_ref)
        self.session.add(new_legacy)
        rec = self.session.query(Legacy).filter_by(ref=new_ref).first()
        return rec

    def get_legacy_table_dict(self):
        """ Get records from the Legacy table """
        self.legacy = {}
        for rec in self.session.query(Legacy).all():
            self.legacy[rec.ref] = rec
        return self.legacy


def main():
    pass


# Runs the script, checking for changes
if __name__ == "__main__":
    main()
