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

def dict_list_required(v):
    if type(v) is not list:
        raise HTTPBadRequest
    return [dict_required(i) for i in v]
