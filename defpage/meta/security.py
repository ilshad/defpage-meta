from sqlalchemy import and_
from defpage.meta.sql import DBSession
from defpage.meta.sql import CollectionUserRole
from defpage.meta.interfaces import ICollection

def security_checker(credentials, request):
    userid = credentials["login"]
    roles = []
    c = ICollection(request.context, None)
    if c:
        cur = DBSession().query(CollectionUserRole).filter(
            and_(CollectionUserRole.collection_id==c.collection_id,
                 CollectionUserRole.user_id==userid)
            ).first()
        if cur:
            roles.append(cur.role)
    return roles
