import json

def init_context(active_nav):
    if active_nav.upper() == 'D':
        active_nav = 'definitions'
    elif active_nav.upper() == 'T':
        active_nav = 'theorems'
    elif active_nav.upper() == 'P':
        active_nav = 'proofs'
    return { 'active_nav': active_nav }

class ListWrapper(object):

    def __init__(self, iterable):
        self._list = list(iterable)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        return self._list[key]

    def __iter__(self):
        return self._list.__iter__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return self.toJSON()

    def json_serializable(self):
        return self._list

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return obj.json_serializable()
        except AttributeError:
            return json.JSONEncoder.default(self, obj)

def json_encode(obj):
    return json.dumps(obj, cls=CustomJSONEncoder)

def json_decode(st):
    return json.loads(st)
