from zope.interface import implementer
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import ForeignKey
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import Allow
from defpage.meta.interfaces import ICollection
from defpage.meta.interfaces import IDocument
from defpage.meta import roles
from defpage.lib.util import random_string
from defpage.lib.util import serialized

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

@implementer(ICollection)
class Collection(Base):

    __tablename__ = "collections"

    __name__ = None
    __parent__ = None

    __acl__ = [(Allow, roles.OWNER, "view"),
               (Allow, roles.OWNER, "manage"),
               (Allow, roles.OWNER, "delete"),

               (Allow, roles.MANAGER, "view"),
               (Allow, roles.MANAGER, "manage"),

               (Allow, roles.GUEST, "view")]

    collection_id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(Unicode)

    _sources = Column(UnicodeText)
    _transmissions = Column(UnicodeText)

    sources = synonym("_sources", descriptor=serialized("_sources"))
    transmissions = synonym("_transmissions", descriptor=serialized("_transmissions"))

    def __init__(self, title):
        self.title = title
        self.collection_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Collection.collection_id)).scalar() or 0)

@implementer(IDocument)
class Document(Base):

    __tablename__ = "documents"

    __name__ = None
    __parent__ = None

    __acl__ = []

    document_id = Column(Integer, primary_key=True, autoincrement=False)
    collection_id = Column(ForeignKey("collections.collection_id"))
    title = Column(Unicode)
    modified = Column(Integer)
    source = Column(Unicode)

    def __init__(self, title, modified):
        self.title = title
        self.modified = modified
        self.document_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Document.document_id)).scalar() or 0)

class CollectionUserRole(Base):

    __tablename__ = "collection_user_roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(ForeignKey("collections.collection_id"))
    user_id = Column(Integer)
    role = Column(String)

    collection = relationship("Collection")

    def __init__(self, collection_id, user_id, role):
        self.collection_id = collection_id
        self.user_id = user_id
        self.role = role

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
