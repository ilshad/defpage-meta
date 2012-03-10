ATTRS = {"gd": {"source":     ["access_token", "refresh_token", "token_expiry"],
                     "collection": ["folder_id"]}}

def detail_attrs(source_type, storage_name):
    return ATTRS[source_type][storage_name]

def make_details(stype, sname, sfrom):
    return dict((x, sfrom[x]) for x in detail_attrs(stype, sname))
