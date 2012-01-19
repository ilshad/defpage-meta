import logging
from sqlalchemy import and_
from pyramid.httpexceptions import HTTPNotFound
from defpage.meta.sql import DBSession
from defpage.meta.config import system_params

meta_logger = logging.getLogger("defpage_meta")

def get_user(req):
    k = req.matchdict['user_id']
    sessions_logger.info("Get user resource: " + unicode(k))
    return {}
