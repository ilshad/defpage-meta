import logging
from sqlalchemy import and_
from pyramid.response import Response
from defpage.meta.sql import DBSession
from defpage.meta.config import system_params
from defpage.meta.sql import Collection
from defpage.meta.sql import Document
from defpage.meta.sql import CollectionACL
from defpage.meta.sql import DocumentACL
from defpage.meta.util import int_required
from defpage.meta.util import dict_required
from defpage.meta.util import int_list_required

meta_logger = logging.getLogger("defpage_meta")

def search_collections(req):
    user_id = int_required(req.GET.get("user_id"))
    dbs = DBSession()
    acls = dbs.query(CollectionACL).filter(CollectionACL.user_id==int(user_id))
    return [{"id":x.collection_id, "title":x.collection.title, "permissions":x.permissions} for x in acls]

def add_collection(req):
    params = req.json_body
    title = params["title"]
    acl = dict_required(params["acl"])
    dbs = DBSession()
    collection = Collection(title)
    collection_id = collection.collection_id
    dbs.add(collection)
    for user_id, permissions in acl.items():
        ob = CollectionACL(collection_id, user_id, permissions)
        dbs.add(ob)
    req.response.status = "201 Created"
    return {"id":collection_id}

def edit_collection(req):
    cid = int_required(req.matchdict["collection_id"])
    params = req.json_body
    title = params.get("title")
    _acl = params.get("acl")
    imports = params.get("imports")
    exports = params.get("exports")
    dbs = DBSession()
    c = dbs.query(Collection).filter(Collection.collection_id==cid).first()
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
