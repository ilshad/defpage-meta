from datetime import datetime
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

class PendingRegistration(Base):

    __tablename__ = "pending_registrations"

    code = Column(String, primary_key=True)
    email = Column(Unicode)
    password = Column(Unicode(), nullable=False)
    created = Column(DateTime)

    def __init__(self, email, password):
        self.code = self._create_code()
        self.email = email
        self.password = make_hash(password)
        self.created = datetime.utcnow()

    def _create_code(self):
        while 1:
            code = random_string(20)
            exists = DBSession().query(PendingRegistration).filter(PendingRegistration.code==code).first()
            if not exists:
                return code

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
