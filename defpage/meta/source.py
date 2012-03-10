ATTRIBUTES = {"gd": {"source": ["access_token", "refresh_token", "token_expiry"],
                "collection": ["folder_id"]}}

def make_details(stype, sname, sfrom):
    return dict((x, sfrom.get(x)) for x in ATTRIBUTES[stype][sname])
