import re
import string
import random
from collections import Counter
import markdown

import logging
logger = logging.getLogger(__name__)

def make_html_safe(st):
    st = st.replace('<', '%lt;')
    st = st.replace('>', '%gt;')
    return st

def normalize_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    name = make_html_safe(name)
    return name

def prepare_tags(primary_tags, other_tags, errors):
    primary_tags = filter(None, map(normalize_tag, primary_tags))
    other_tags   = filter(None, map(normalize_tag, other_tags))
    tag_counter = Counter(primary_tags) + Counter(other_tags)
    duplicates = [p[0] for p in tag_counter.iteritems() if p[1] > 1]
    if duplicates:
        errors['Duplicate tags'] = duplicates
        return None
    tags = {}
    tags.update(dict.fromkeys(primary_tags, True))
    tags.update(dict.fromkeys(other_tags, False))
    return tags

def prepare_body(body, errors):
    body = make_html_safe(body.strip())
    return body

SHORT_NAME_CHARS = '23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
#SHORT_NAME_CHARS = ''.join(set(string.ascii_letters + string.digits) - set('0oO1lI'))

def make_short_name(length):
    return ''.join(random.choice(SHORT_NAME_CHARS) for _ in range(length))

def typeset_body(st):
    secret = make_short_name(8)
    parts = st.split('$$')
    maths = []
    for i in range(len(parts)):
        if i % 2 == 1:
            key = secret + "=" + str(i)
            maths.append((key, '\[' + parts[i] + '\]'))
            parts[i] = '\n\n' + key + '\n\n'
        else:
            parts2 = parts[i].split('$')
            for j in range(len(parts2)):
                if j % 2 == 1:
                    key = secret + "-" + str(i)
                    maths.append((key, '\(' + parts2[j] + '\)'))
                    parts2[j] = key
            parts[i] = ''.join(parts2)
    st = ''.join(parts)
    st = markdown.markdown(st)
    for (old, new) in maths:
        st = st.replace(old, new)
    return st

def typeset_tag(st):
    parts = st.split('$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\(' + parts[i] + '\)'
    return ''.join(parts)

