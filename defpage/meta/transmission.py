# SQL database - integer id.
# REST service API is string name.
_TYPES = {1:"rest",
          2:"dirty"}

def _get_key(name):
    for k,v in _TYPES.items():
        if v == name:
            return k

def type_encoded(k):
    def _get(inst):
        return _TYPES[getattr(inst, k)]
    def _set(inst, v):
        setattr(inst, k, _get_key(v))
    return property(_get, _set)
