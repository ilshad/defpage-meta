import logging
from sqlalchemy import and_
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
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
    params = req.json_body
    title = params.get("title")
    acl = params.get("acl")
    imports = params.get("imports")
    exports = params.get("exports")
    cid = req.context.collection_id
    if title:
        req.context.title = title
    if acl:
        acl = dict_required(acl)
        for userid, permissions in acl.items():
            q = and_(CollectionACL.collection_id==cid, CollectionACL.user_id==userid)
            old = dbs.query(CollectionACL).filter(q).first()
            if old:
                if old.permissions:
                    if set(old.permissions) == set(permissions):
                        continue
                dbs.delete(old)
            dbs.add(CollectionACL(cid, userid, permissions))
    if imports:
        req.context.imports = int_list_required(imports)
    if exports:
        req.context.exports = int_list_required(exports)
    return Response(status="204 No Content")

ALLOW_DELETE = ("gd")

def del_collection(req):
    dbs = DBSession()
    cid = req.context.collection_id
    acls = dbs.query(CollectionACL).filter(CollectionACL.collection_id==cid)
    for i in acls:
        dbs.delete(i)
    docs = dbs.query(Document).filter(Document.collection_id==cid)
    for doc in docs:
        control = doc.control.split(":", 1)
        if control[0] in ALLOW_DELETE:
            dbs.delete(doc)
    dbs.delete(req.context)
    return Response(status="204 No Content")

def get_collection(req):
    dbs = DBSession()
    c = req.context
    cid = c.collection_id
    acl_query = dbs.query(CollectionACL).filter(CollectionACL.collection_id==cid)
    acl = dict((i.user_id, i.permissions) for i in acl_query)
    docs_query = dbs.query(Document).filter(Document.collection_id==cid)
    docs = [{"id":i.document_id, "title":i.title, "modified":datetime_format(i.modified), "control":i.control} for i in docs_query]
    return {"title":c.title, "imports":c.imports, "exports":c.exports, "acl":acl, "documents":docs}

def search_collections(req):
    user_id = int_required(req.GET.get("user_id"))
    dbs = DBSession()
    acls = dbs.query(CollectionACL).filter(CollectionACL.user_id==int(user_id))
    return [{"id":x.collection_id, "title":x.collection.title, "permissions":x.permissions} for x in acls]

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

def edit_document(req):
    modified = False
    params = req.json_body
    title = params.get("title")
    control = params.get("control")
    cid = params.get("collection")
    if cid:
        cid = int_required(cid)
    acl = params.get("acl")
    if acl:
        acl = dict_required(acl)
    dbs = DBSession()
    if title:
        req.context.title = title
        modified = True
    if control:
        req.context.control = control
        modified = True
    if cid:
        if not bool(dbs.query(Collection.collection_id).filter(Collection.collection_id==cid).count()):
            raise HTTPBadRequest
        req.context.collection_id = cid
        modified = True
    if acl:
        for userid, permissions in acl.items():
            q = and_(DocumentACL.document_id==docid, DocumentACL.user_id==userid)
            old = dbs.query(DocumentACL).filter(q).first()
            if old:
                if old.permissions:
                    if set(old.permissions) == set(permissions):
                        continue
                dbs.delete(old)
            dbs.add(DocumentACL(cid, userid, permissions))
            modified = True
    if modified:
        req.context.update()
    return Response(status="204 No Content")

def del_document(req):
    dbs = DBSession()
    acls = dbs.query(DocumentACL).filter(DocumentACL.document_id==req.context.document_id)
    for i in acls:
        dbs.delete(i)
    dbs.delete(req.context)
    return Response(status="204 No Content")

def get_document(req):
    dbs = DBSession()
    acl_query = dbs.query(DocumentACL).filter(DocumentACL.document_id==docid)
    acl = dict((i.user_id, i.permissions) for i in acl_query)
    return {"title":doc.title, "modified":datetime_format(doc.modified), "control":doc.control, "collection":doc.collection_id, "acl":acl}
