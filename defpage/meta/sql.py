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
    source_id = Column(Integer)

    # (GD) dict -> folder_id::String
    _source_details = Column("source_details", UnicodeText)
    source_details = synonym("_source_details", descriptor=serialized("_source_details"))

    _transmissions = Column("transmissions", UnicodeText)
    transmissions = synonym("_transmissions", descriptor=serialized("_transmissions"))

    def __init__(self, title):
        self.title = title
        self.collection_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Collection.collection_id)).scalar() or 0)

class Source(Base):

    __tablename__ = "sources"

    source_id = Column(Integer, primary_key=True, autoincrement=False)

    source_type = Column(Unicode)
    user_id = Column(Integer)

    # (GD) dict -> access_token::String, refresh_token::String, token_expiry::Integer
    _source_details = Column("source_details", UnicodeText)
    source_details = synonym("_source_details", descriptor=serialized("_source_details"))

    def __init__(self, source_type, user_id):
        self.source_type = source_type
        self.user_id = user_id
        self.source_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Source.source_id)).scalar() or 0)

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

    _source = Column(Unicode)

    source = synonym("_source", descriptor=serialized("_source"))

    def __init__(self, title, modified):
        self.title = title
        self.modified = modified
        self.document_id = self._create_id()

    def _create_id(self):
        return 1 + (DBSession().query(func.max(Document.document_id)).scalar() or 0)

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
