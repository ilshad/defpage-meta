from sqlalchemy import and_
from pyramid.httpexceptions import HTTPNotFound
from defpage.meta.sql import DBSession
from defpage.meta.sql import Collection
from defpage.meta.sql import Document
from defpage.meta.sql import Source

def get_collection(req):
    v = DBSession().query(Collection).filter(
        Collection.id==int(req.matchdict["name"])).scalar()
    if not v:
        raise HTTPNotFound
    return v

def get_document(req):
    v = DBSession().query(Document).filter(
        Document.id==int(req.matchdict["name"])).scalar()
    if not v:
        raise HTTPNotFound
    return v

def get_source(req):
    v =  DBSession().query(Source).filter(and_(
            Source.user_id==int(req.matchdict["name"]),
            Source.source_type==req.matchdict["source_type"])).scalar()
    if not v:
        raise HTTPNotFound
    return v
