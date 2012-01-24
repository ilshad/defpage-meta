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

def int_list_required(v):
    if type(v) is not list:
        raise HTTPBadRequest
    return [int_required(i) for i in v]

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def datetime_format(dt):
    return dt.strftime(DATETIME_FORMAT)
