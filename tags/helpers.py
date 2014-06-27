import re
from main.helpers import ListWrapper

def clean_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    return name

def normalize_tag(name):
    return clean_tag(name).lower()

class CategoryCollection(ListWrapper):

    def __init__(self, categories):
        super().__init__(categories)

    def json_data(self):
        return [c.json_data() for c in self]
