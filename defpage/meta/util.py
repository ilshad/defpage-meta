import json
import random
import string
import pyramid.httpexceptions

def random_string(length):
    chars = []
    while length:
        chars.extend(random.sample(string.letters+string.digits, 1))
        length -= 1
    return "".join(chars)

def serialized(k):
    def _get(inst):
        return json.loads(getattr(inst, k))
    def _set(inst, v):
        setattr(inst, k, json.dumps(v))
    return property(_get, _set)

def int_required(v):
    try:
        return int(v)
    except TypeError:
        raise pyramid.httpexceptions.HTTPBadRequest
    except ValueError:
        raise pyramid.httpexceptions.HTTPBadRequest
