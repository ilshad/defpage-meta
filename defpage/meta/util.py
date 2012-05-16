from pyramid.httpexceptions import HTTPBadRequest

def int_required(v):
    try:
        return int(v)
    except TypeError:
        raise HTTPBadRequest
    except ValueError:
        raise HTTPBadRequest

def dict_required(v):
    if type(v) is dict:
        return v
    raise HTTPBadRequest

def list_required(v):
    if type(v) is list:
        return v
    raise HTTPBadRequest

def is_equal_items(d1, d2):
    if not d1:
        return False
    for k,v in d1.items():
        try:
            if d2[k] != v:
                return False
        except KeyError:
            return False
    return True
