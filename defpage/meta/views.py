import logging
from sqlalchemy import and_
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from defpage.meta.sql import DBSession
from defpage.meta.config import system_params
from defpage.meta.sql import Collection
from defpage.meta.sql import Document
from defpage.meta.sql import CollectionACL
from defpage.meta.sql import DocumentACL
from defpage.meta.util import int_required
from defpage.meta.util import dict_required
from defpage.meta.util import int_list_required
from defpage.meta.util import datetime_format

meta_logger = logging.getLogger("defpage_meta")

def search_collections(req):
    user_id = int_required(req.GET.get("user_id"))
    dbs = DBSession()
    acls = dbs.query(CollectionACL).filter(CollectionACL.user_id==int(user_id))
    return [{"id":x.collection_id, "title":x.collection.title, "permissions":x.permissions} for x in acls]

def get_collection(req):
    cid = int_required(req.matchdict["collection_id"])
    dbs = DBSession()
    c = dbs.query(Collection).filter(Collection.collection_id==cid).first()
    if not c:
        raise HTTPNotFound
    acl_query = dbs.query(CollectionACL).filter(CollectionACL.collection_id==cid)
    acl = dict((i.user_id, i.permissions) for i in acl_query)
    docs_query = dbs.query(Document).filter(Document.collection_id==cid)
    docs = [{"id":i.document_id, "title":i.title, "modified":datetime_format(i.modified), "control":i.control} for i in docs_query]
    return {"title":c.title, "imports":c.imports, "exports":c.exports, "acl":acl, "documents":docs}

def add_collection(req):
    params = req.json_body
    title = params["title"]
    acl = dict_required(params["acl"])
    dbs = DBSession()
    collection = Collection(title)
    cid = collection.collection_id
    dbs.add(collection)
    for userid, permissions in acl.items():
        ob = CollectionACL(cid, userid, permissions)
        dbs.add(ob)
    req.response.status = "201 Created"
    return {"id":cid}

def edit_collection(req):
    cid = int_required(req.matchdict["collection_id"])
    params = req.json_body
    title = params.get("title")
    _acl = params.get("acl")
    imports = params.get("imports")
    exports = params.get("exports")
    dbs = DBSession()
    c = dbs.query(Collection).filter(Collection.collection_id==cid).first()
    if not c:
        raise HTTPNotFound
    if title:
        c.title = title
    if _acl:
        acl = dict_required(_acl)
        for user_id, permissions in acl.items():
            q = and_(CollectionACL.collection_id==cid, CollectionACL.user_id==user_id)
            old = dbs.query(CollectionACL).filter(q).first()
            if old:
                if old.permissions:
                    if set(old.permissions) == set(permissions):
                        continue
                dbs.delete(old)
            dbs.add(CollectionACL(cid, user_id, permissions))
    if imports:
        c.imports = int_list_required(imports)
    if exports:
        c.exports = int_list_required(exports)
    return Response(status="204 No Content")

ALLOW_DELETE = ("gd")

def del_collection(req):
    cid = int_required(req.matchdict["collection_id"])
    dbs = DBSession()
    c = dbs.query(Collection).filter(Collection.collection_id==cid).first()
    if not c:
        raise HTTPNotFound
    acls = dbs.query(CollectionACL).filter(CollectionACL.collection_id==cid)
    for i in acls:
        dbs.delete(i)
    docs = dbs.query(Document).filter(Document.collection_id==cid)
    for doc in docs:
        control = doc.control.split(":", 1)
        if control[0] in ALLOW_DELETE:
            dbs.delete(doc)
    dbs.delete(c)
    return Response(status="204 No Content")

def add_document(req):
    params = req.json_body

    # check title
    try:
        title = params["title"]
    except KeyError:
        raise HTTPBadRequest

    # check collecton
    cid = params.get("collection")
    if cid is not None:
        try:
            cid = int(cid)
        except ValueError:
            raise HTTPBadRequest

    # check ACL
    try:
        acl = dict_required(params["acl"])
    except KeyError:
        raise HTTPBadRequest
    success = False
    for k,v in acl.items():
        if type(v) is not list:
            raise HTTPBadRequest
        if "owner" in v:
            success = True
            break
    if not success:
        raise HTTPBadRequest

    dbs = DBSession()
    doc = Document(title)
    docid = doc.document_id
    if cid:
        doc.collection_id = cid
    dbs.add(doc)
    for userid, permissions in acl.items():
        ob = DocumentACL(docid, userid, permissions)
        dbs.add(ob)
    req.response.status = "201 Created"
    return {"id":docid}
