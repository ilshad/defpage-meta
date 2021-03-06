import logging
import transaction
from sqlalchemy import and_
from sqlalchemy.sql import func
from sqlalchemy.sql import exists
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import authenticated_userid
from defpage.meta.sql import DBSession
from defpage.meta.config import system_params
from defpage.meta.sql import Collection
from defpage.meta.sql import Document
from defpage.meta.sql import Source
from defpage.meta.sql import CollectionUserRole
from defpage.meta.sql import Transmission
from defpage.meta.sql import Entry
from defpage.meta.util import int_required
from defpage.meta.util import dict_required
from defpage.meta.util import list_required
from defpage.meta.util import is_equal_items
from defpage.meta.source import make_details

meta_logger = logging.getLogger("defpage_meta")

def add_collection(req):
    params = req.json_body
    try:
        title = params["title"]
        userid = int_required(params["owner"])
    except KeyError:
        raise HTTPBadRequest
    dbs = DBSession()
    c = Collection(title)
    dbs.add(c)
    dbs.flush()
    dbs.add(CollectionUserRole(c.id, userid, u"owner"))
    req.response.status = "201 Created"
    return {"id":c.id}

def edit_collection(req):
    userid = authenticated_userid(req)
    dbs = DBSession()
    params = req.json_body
    title = params.get("title")
    source = params.get("source")
    roles = params.get("roles")
    if title:
        req.context.title = title

    #################################
    #
    # Configure source for collection
    #
    #################################
    if source:
        source = dict_required(source)
        stype = source["type"]
        if not req.context.source_id:
            # Define source.
            # User id should be real, not system user.
            userid = int_required(userid)
            s = dbs.query(Source).filter(and_(
                    Source.user_id==userid,
                    Source.source_type==stype
                    )).scalar()
            if not s:
                # There is no such source for this {user id, source type},
                # so create new source.
                s = Source(stype, userid)
                s.source_details = make_details(stype, "source", source)
                dbs.add(s)
                dbs.flush()
                req.context.source_id = s.id
                req.context.source_details = make_details(stype, "collection", source)
            else:
                # Assign existing source to this colllection.
                req.context.source_id = s.id
                req.context.source_details = make_details(stype, "collection", source)
        else:
            # Update already configured collection source data.
            # User id can be system, therefore do not pass userid into database.
            s = dbs.query(Source).filter(Source.id==req.context.source_id).scalar()
            if not is_equal_items(s.source_details, source):
                s.source_details = make_details(stype, "source", source)
            if not is_equal_items(req.context.source_details, source):
                req.context.source_details = make_details(stype, "collection", source)
    cid = req.context.id
    if roles:
        roles = dict_required(roles)
        if u"owner" not in roles.values():
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
    cid = req.context.id
    roles = dbs.query(CollectionUserRole).filter(CollectionUserRole.collection_id==cid)
    for r in roles:
        dbs.delete(r)
    docs = dbs.query(Document).filter(Document.collection_id==cid)
    for d in docs:
        if d.source["type"] in ALLOW_DELETE:
            for e in dbs.query(Entry).filter(Entry.document_id==d.id):
                dbs.delete(e)
    transaction.commit()
    for d in docs:
        if d.source["type"] in ALLOW_DELETE:
            dbs.delete(d)
    transmissions = dbs.query(Transmission).filter(Transmission.collection_id==cid)
    for t in transmissions:
        dbs.delete(t)
    transaction.commit()
    dbs.delete(req.context)
    return Response(status="204 No Content")

def get_collection(req):
    dbs = DBSession()
    c = req.context
    cid = c.id
    roles = dict((i.user_id, i.role) for i in dbs.query(CollectionUserRole).filter( 
            CollectionUserRole.collection_id==cid))
    count_doc = dbs.query(Document.id).filter(Document.collection_id==cid).count()
    count_trs = dbs.query(Transmission.id).filter(Transmission.collection_id==cid).count()
    source = {}
    if c.source_id:
        s = dbs.query(Source).filter(Source.id==c.source_id).scalar()
        source.update(s.source_details)
        source.update(c.source_details or {})
        source["type"] = s.source_type
    return {"title":c.title,
            "source":source or None,
            "roles":roles,
            "count_documents":count_doc,
            "count_transmissions":count_trs}

def get_collection_documents(req):
    cid = req.context.id
    return [{"id":i.id,
             "title":i.title,
             "modified":i.modified,
             "version":i.version,
             "source":i.source}
            for i in DBSession().query(Document).filter(Document.collection_id==cid)]

def search_collections(req):
    userid = req.GET.get("user_id")
    info = req.GET.get("info")
    if userid:
        r = DBSession().query(CollectionUserRole).filter(
            CollectionUserRole.user_id==int_required(userid))
        return [{"id":x.collection_id,
                 "title":x.collection.title,
                 "role":x.role}
                for x in r]
    elif info == "total_num":
        return {"total_num": DBSession().query(Collection.id).count()}
    elif info == "max_id":
        return {"max_id": DBSession().query(func.max(Collection.id)).scalar()}

def add_document(req):
    params = req.json_body
    title = params.get("title")
    source = params.get("source")
    cid = params.get("collection_id")
    modified = params.get("modified")
    if (title is None) \
            or (modified is None) \
            or (source is None) \
            or (cid is None) \
            or (modified is None):
        raise HTTPBadRequest
    if cid:
        cid = int_required(cid)
    dbs = DBSession()
    doc = Document(title, source, cid, modified)
    dbs.add(doc)
    dbs.flush()
    req.response.status = "201 Created"
    return {"id":doc.id}

def edit_document(req):
    params = req.json_body
    title = params.get("title")
    source = params.get("source")
    cid = params.get("collection_id")
    modified = params.get("modified")
    if title:
        req.context.title = title
    if cid:
        req.context.collection_id = int_required(cid)
    if modified:
        req.context.modified = int_required(modified)
        req.context.version += 1
    if source:
        req.context.source = source
    return Response(status="204 No Content")

def del_document(req):
    DBSession().delete(req.context)
    return Response(status="204 No Content")

def get_document(req):
    return {"title":req.context.title,
            "modified":req.context.modified,
            "version":req.context.version,
            "source":req.context.source,
            "collection_id":req.context.collection_id}

def set_source(req):
    params = req.json_body
    cid = int_required(params.get("collection_id"))
    c = DBSession().query(Collection).filter(Collection.id==cid).scalar()
    if c.source_id and (params.get("force") is not True):
        raise HTTPForbidden
    c.source_id = req.context.id
    return Response(status="204 No Content")

def add_transmission(req):
    d = req.json_body
    DBSession().add(Transmission(req.context.id, d["type"], d["description"], d["params"]))
    return Response(status="204 No Content")

def get_collection_transmissions(req):
    return [{"id":x.id,
             "type":x.type_name,
             "description":x.description,
             "params":x.params
             } for x in DBSession().query(Transmission).filter(
            Transmission.collection_id==req.context.id)]

def get_transmission(req):
    o = DBSession().query(Transmission).filter(Transmission.id==req.matchdict["id"]).scalar()
    if not o:
        raise HTTPNotFound
    return {"type":o.type_name,
            "description":o.description,
            "params":o.params}

def put_transmission(req):
    o = DBSession().query(Transmission).filter(Transmission.id==req.matchdict["id"]).scalar()
    if not o:
        raise HTTPNotFound
    d = req.json_body
    try:
        tp, ds, pr = d["type"], d["description"], d["params"]
    except KeyError:
        raise HTTPBadRequest
    o.type_name = tp
    o.description = ds
    o.params = pr
    return Response(status="204 No Content")

def delete_transmission(req):
    dbs = DBSession()
    o = dbs.query(Transmission).filter(Transmission.id==req.matchdict["id"]).scalar()
    if not o:
        raise HTTPNotFound
    dbs.delete(o)
    return Response(status="204 No Content")

def get_document_transmissions_directory(req):
    dbs = DBSession()
    r = []
    for t in dbs.query(Transmission).filter(
        Transmission.collection_id==req.context.collection_id):
        entry = dbs.query(Entry).filter(
            and_(Entry.document_id==req.context.id,
                 Entry.transmission_id==t.id)).scalar()
        r.append({"id": t.id,
                  "hostdoc_id": entry and entry.hostdoc_id or None,
                  "created": entry and entry.created or 0,
                  "modified": entry and entry.modified or 0,
                  "version": entry and entry.version or 0,
                  "type": t.type_name,
                  "description": t.description,
                  "params": t.params})
    return r

def get_document_transmission(req):
    dbs = DBSession()
    t = dbs.query(Transmission).filter(Transmission.id==req.matchdict["id"]).scalar()
    if t is None:
        raise HTTPNotFound
    entry = dbs.query(Entry).filter(and_(
        Entry.document_id==req.context.id,
        Entry.transmission_id==t.id)).scalar()
    return {"hostdoc_id": entry and entry.hostdoc_id or None,
            "created": entry and entry.created or 0,
            "modified": entry and entry.modified or 0,
            "version": entry and entry.version or 0,
            "type": t.type_name,
            "description": t.description,
            "params": t.params}

def add_document_transmission(req):
    params = req.json_body
    tid = params.get("transmission_id")
    hostdoc_id = params.get("hostdoc_id")
    created = params.get("created")
    version = params.get("version")
    if (tid is None) \
            or (hostdoc_id is None) \
            or (created is None) \
            or (version is None):
        raise HTTPBadRequest
    DBSession().add(Entry(req.context.id, tid, hostdoc_id, created, version))
    return Response(status="204 No Content")

def update_document_transmission(req):
    params = req.json_body
    modified = params.get("modified")
    version = params.get("version")
    if (modified is None) or (version is None):
        raise HTTPBadRequest
    entry = DBSession().query(Entry).filter(
        and_(Entry.document_id==req.context.id,
             Entry.transmission_id==req.matchdict["id"])
        ).scalar()
    entry.update(modified, version)
    return Response(status="204 No Content")

def delete_document_transmission(req):
    dbs = DBSession()
    entry = dbs.query(Entry).filter(
        and_(Entry.document_id==req.context.id,
             Entry.transmission_id==req.matchdict["id"])
        ).scalar()
    dbs.delete(entry)
    return Response(status="204 No Content")
