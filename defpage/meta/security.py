from sqlalchemy import and_
from defpage.meta.sql import DBSession
from defpage.meta.sql import CollectionUserRole
from defpage.meta.interfaces import ICollection
from defpage.meta.config import system_params
from defpage.meta.roles import OWNER

def security_checker(credentials, request):
    roles = []
    userid = credentials["login"]
    if userid:
        if userid == system_params.system_user:
            roles.append(OWNER)
        else:
            c = ICollection(request.context, None)
            if c:
                cur = DBSession().query(CollectionUserRole).filter(
                    and_(CollectionUserRole.collection_id==c.id,
                         CollectionUserRole.user_id==userid)
                    ).first()
                if cur:
                    roles.append(cur.role)
    return roles
