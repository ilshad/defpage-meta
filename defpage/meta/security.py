from sqlalchemy import and_
from defpage.meta.sql import DBSession
from defpage.meta.sql import CollectionUserRole
from defpage.meta.interfaces import ICollection

def security_checker(credentials, request):
    userid = credentials["login"]
    roles = []
    c = ICollection(request.context, None)
    if c:
        r = DBSession().query(CollectionUserRole.role).filter(
            and_(CollectionUserRole.collection_id==c.collection_id, CollectionUserRole.user_id==userid)
            ).first()
        if r:
            roles.append(r)
    return roles
