# SQL database - integer id.
# REST service API is string name.
TYPES = {1:"rest",
         2:"dirty"}

def get_type_id(name):
    for k,v in TYPES.items():
        if v == name:
            return k
