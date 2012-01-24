from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym
from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from zope.sqlalchemy import ZopeTransactionExtension
from defpage.lib.util import random_string
from defpage.lib.util import serialized

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

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

class CollectionACL(Base):

    __tablename__ = "collection_acl"

    acl_id = Column(Integer, primary_key=True, autoincrement=True)
    collection_id = Column(ForeignKey("collections.collection_id"))
    user_id = Column(Integer)

    _permissions = Column(Unicode)

    permissions = synonym("_permissions", descriptor=serialized("_permissions"))
    collection = relationship("Collection")

    def __init__(self, collection_id, user_id, permissions):
        self.collection_id = collection_id
        self.user_id = user_id
        self.permissions = permissions

class DocumentACL(Base):

    __tablename__ = "document_acl"

    acl_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(ForeignKey("documents.document_id"))
    user_id = Column(Integer)

    _permissions = Column(Unicode)

    permissions = synonym("_permissions", descriptor=serialized("_permissions"))
    document = relationship("Document")

    def __init__(self, document_id, user_id, permissions):
        self.document_id = document_id
        self.user_id = user_id
        self.permissions = permissions

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
