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
from sqlalchemy import ForeignKey
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import Allow
from defpage.lib.util import random_string
from defpage.lib.util import serialized
from defpage.meta.interfaces import ICollection
from defpage.meta.interfaces import IDocument
from defpage.meta.transmission import type_encoded
from defpage.meta import roles

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

@implementer(ICollection)
class Collection(Base):

    __tablename__ = "collection"

    __name__ = None
    __parent__ = None

    __acl__ = [(Allow, roles.OWNER, "view"),
               (Allow, roles.OWNER, "manage"),
               (Allow, roles.OWNER, "delete"),

               (Allow, roles.MANAGER, "view"),
               (Allow, roles.MANAGER, "manage"),

               (Allow, roles.GUEST, "view")]

    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    source_id = Column(Integer)

    _source_details = Column("source_details", UnicodeText)
    source_details = synonym("_source_details", descriptor=serialized("_source_details"))

    def __init__(self, title):
        self.title = title

class Source(Base):

    __tablename__ = "source"

    id = Column(Integer, primary_key=True)
    source_type = Column(Unicode)
    user_id = Column(Integer)

    _source_details = Column("source_details", UnicodeText)
    source_details = synonym("_source_details", descriptor=serialized("_source_details"))

    def __init__(self, source_type, user_id):
        self.source_type = source_type
        self.user_id = user_id

class Transmission(Base):

    __tablename__ = "transmission"

    id = Column(Integer, primary_key=True)

    collection_id = Column(ForeignKey("collection.id"))
    description = Column(Unicode)

    _tid = Column("type_id", Integer)
    type_name = synonym("_tid", descriptor=type_encoded("_tid"))

    _params = Column("params", UnicodeText)
    params = synonym("_params", descriptor=serialized("_params"))

    def __init__(self, collection_id, type_name, description, params):
        self.collection_id = collection_id
        self.type_name = type_name
        self.description = description
        self.params = params

class CollectionUserRole(Base):

    __tablename__ = "collection_user_role"

    id = Column(Integer, primary_key=True)
    collection_id = Column(ForeignKey("collection.id"))
    user_id = Column(Integer)
    role = Column(Unicode)

    collection = relationship("Collection")

    def __init__(self, collection_id, user_id, role):
        self.collection_id = collection_id
        self.user_id = user_id
        self.role = role

@implementer(IDocument)
class Document(Base):

    __tablename__ = "document"

    __name__ = None
    __parent__ = None

    __acl__ = []

    id = Column(Integer, primary_key=True)
    collection_id = Column(ForeignKey("collection.id"))
    title = Column(Unicode)
    modified = Column(Integer)
    version = Column(Integer)

    _source = Column("source", Unicode)
    source = synonym("_source", descriptor=serialized("_source"))

    def __init__(self, title, source, collection_id, modified):
        self.title = title
        self.source = source
        self.collection_id = collection_id
        self.modified = modified
        self.version = 1

class Entry(Base):

    __tablename__ = "entry"

    id = Column(Integer, primary_key=True)
    document_id = Column(ForeignKey("document.id"))    
    transmission_id = Column(ForeignKey("transmission.id"))
    hostdoc_id = Column(Unicode)
    created = Column(Integer)
    modified = Column(Integer)
    version = Column(Integer)

    def __init__(self, document_id, transmission_id, hostdoc_id, created, version):
        self.document_id = document_id
        self.transmission_id = transmission_id
        self.hostdoc_id = hostdoc_id
        self.created = created
        self.modified = 0
        self.version = version

    def update(self, modified, version):
        self.modified = modified
        self.version = version

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
