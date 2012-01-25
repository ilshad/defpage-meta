from defpage.meta import sql

class Collections(dict):

    __name__ = "collections"
    __parent__ = None
    __acl__ = []

    def __getitem__(self, name):
        dbs = sql.DBSession()
        v = dbs.query(sql.Collection).filter(sql.Collection.collection_id==str(name)).first()
        v.__name__ = name
        v.__parent__ = self
        return v

class Documents(dict):

    __name__ = "documents"
    __parent__ = None
    __acl__ = []

    def __getitem__(self, name):
        dbs = sql.DBSession()
        v = dbs.query(sql.Document).filter(sql.Document.document_id==str(name)).first()
        v.__name__ = name
        v.__parent__ = self
        return v

class Root(dict):

    __name__ = None
    __parent__ = None
    __acl__ = []

    def __init__(self):
        self["collections"] = Collections()
        self["collections"].__parent__ = self

        self["documents"] = Documents()
        self["documents"].__parent__ = self

root = Root()

def root_factory(req):
    return root
