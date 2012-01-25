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
from defpage.meta.sql import CollectionUserRole
from defpage.meta.util import int_required
from defpage.meta.util import dict_required
from defpage.meta.util import int_list_required
from defpage.meta.util import datetime_format

meta_logger = logging.getLogger("defpage_meta")

def add_collection(req):
    params = req.json_body
    title = params["title"]
    userid = int_required(params["owner"])
    dbs = DBSession()
    c = Collection(title)
    cid = c.collection_id
    dbs.add(c)
    dbs.add(CollectionUserRole(cid, userid, "owner"))
    req.response.status = "201 Created"
    return {"id":cid}

def edit_collection(req):
    params = req.json_body
    title = params.get("title")
    sources = params.get("sources")
    transmissions = params.get("transmissions")
    roles = params.get("roles")
    if title:
        req.context.title = title
    if sources:
        req.context.sources = int_list_required(sources)
    if transmissions:
        req.context.transmissions = int_list_required(transmissions)
    cid = req.context.collection_id
    if roles:
        dbs = DBSession()
        roles = dict_required(roles)
        if "owner" not in roles.values():
            raise HTTPBadRequest
        for i in dbs.query(CollectionUserRole).filter(
            CollectionUserRole.collection_id==cid):
            dbs.delete(i)
        for userid, role in roles.items():
            dbs.add(CollectionUserRole(cid, userid, role))
    return Response(status="204 No Content")

ALLOW_DELETE = ("gd")

def del_collection(req):
    dbs = DBSession()
    cid = req.context.collection_id
    roles = dbs.query(CollectionUserRole).filter(CollectionUserRole.collection_id==cid)
    for r in roles:
        dbs.delete(r)
    docs = dbs.query(Document).filter(Document.collection_id==cid)
    for d in docs:
        control = d.source.split(":", 1)
        if control[0] in ALLOW_DELETE:
            dbs.delete(d)
    dbs.delete(req.context)
    return Response(status="204 No Content")

def get_collection(req):
    dbs = DBSession()
    c = req.context
    cid = c.collection_id
    roles = dict((i.user_id, i.role) for i in dbs.query(CollectionUserRole).filter(
            CollectionUserRole.collection_id==cid))
    docs = [{"id":i.document_id,
             "title":i.title,
             "modified":datetime_format(i.modified),
             "source":i.source}
            for i in dbs.query(Document).filter(Document.collection_id==cid)]
    return {"title":c.title,
            "sources":c.sources,
            "transmissions":c.transmissions,
            "roles":roles,
            "documents":docs}

def search_collections(req):
    userid = int_required(req.GET.get("user_id"))
    r = DBSession().query(CollectionUserRole).filter(CollectionUserRole.user_id==int(userid))
    return [{"id":x.collection_id, "title":x.collection.title, "role":x.role} for x in r]

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
