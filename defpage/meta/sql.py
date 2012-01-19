import json
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import synonym
from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from zope.sqlalchemy import ZopeTransactionExtension
from defpage.meta.util import random_string

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

def serialized(k):
    def _get(inst):
        return json.loads(getattr(inst, k))
    def _set(inst, v):
        setattr(inst, k, json.dumps(v))
    return property(_get, _set)

class Collection(Base):

    __tablename__ = "collections"

    collection_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(Unicode)

    _imports = Column(Unicode)
    _exports = Column(Unicode)

    imports = synonym("_imports", descriptor=serialized("_imports"))
    exports = synonym("_exports", descriptor=serialized("_exports"))

    def __init__(self, title):
        self.title = title
        self.collection_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Collection.collection_id)).scalar() or 0)

class Document(Base):

    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=False)
    collection_id = Column(ForeignKey("collections.collection_id"))
    title = Column(Unicode)
    modified = Column(DateTime)
    control = Column(Unicode)

    def __init__(self, title):
        self.title = title
        self.document_id = self._create_id()
        self.update()

    def update(self):
        self.modified = datetime.utcnow()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Document.document_id)).scalar() or 0)

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
