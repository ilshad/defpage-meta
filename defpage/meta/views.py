import logging
from sqlalchemy import and_
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPBadRequest
from defpage.meta.sql import DBSession
from defpage.meta.config import system_params

meta_logger = logging.getLogger("defpage_meta")

def search_collections(req):
    user_id = req.GET.get("user_id")
    if not user_id:
        raise HTTPBadRequest
    sessions_logger.info("Get collections for user: " + unicode(k))
    return {}
