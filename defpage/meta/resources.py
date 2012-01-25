from pyramid.httpexceptions import HTTPNotFound
from defpage.meta.sql import DBSession
from defpage.meta.sql import Collection
from defpage.meta.sql import Document

def get_collection(req):
    v = DBSession().query(Collection).filter(Collection.collection_id==int(req.matchdict["name"])).first()
    if not v:
        raise HTTPNotFound
    return v

def get_document(req):
    v = DBSession().query(Document).filter(Document.document_id==int(req.matchdict["name"])).first()
    if not v:
        raise HTTPNotFound
    return v
