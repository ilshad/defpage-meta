from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import DateTime
from zope.sqlalchemy import ZopeTransactionExtension
from defpage.meta.util import random_string

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

class Collection(Base):

    __tablename__ = "collections"

    collection_id = Coluemn(Integer, primary_key=True, autoincrement=False)

    title = Column(Unicode)

    imp = Column(String)
    exp = Column(String)

    def __init__(self, title):
        self.title = title
        self.collection_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Collection.collection_id)).scalar() or 0)

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
