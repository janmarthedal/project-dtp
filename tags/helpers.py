import re

def clean_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    return name

def normalize_tag(name):
    return clean_tag(name).lower()

class CategoryList:

    def __init__(self, categories):
        self._categories = categories
        
    def __len__(self):
        return len(self._categories)
    
    def __getitem__(self, key):
        return self._categories[key]
    
    def __iter__(self):
        return self._categories.__iter__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        return self.toJSON()

    def toJSON(self):
        return u'[%s]' % u','.join([category.toJSON() for category in self._categories])
