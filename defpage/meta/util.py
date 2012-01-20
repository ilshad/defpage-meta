import json
import random
import string
from pyramid.httpexceptions import HTTPBadRequest

def random_string(length):
    chars = []
    while length:
        chars.extend(random.sample(string.letters+string.digits, 1))
        length -= 1
    return "".join(chars)

def serialized(k):
    def _get(inst):
        return json.loads(getattr(inst, k) or u'null')
    def _set(inst, v):
        setattr(inst, k, json.dumps(v))
    return property(_get, _set)

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
