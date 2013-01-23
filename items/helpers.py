import re
import string
from collections import Counter
from django.template.loader import get_template
from django.template import Context
from django.utils.crypto import get_random_string
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

def prepare_tags(primary_tags, other_tags, messages):
    primary_tags = filter(None, map(normalize_tag, primary_tags))
    other_tags   = filter(None, map(normalize_tag, other_tags))
    tag_counter = Counter(primary_tags) + Counter(other_tags)
    duplicates = [p[0] for p in tag_counter.iteritems() if p[1] > 1]
    if duplicates:
        t = get_template('inline/taglist.html')
        c = Context({'header':  'Tag duplicates:',
                     'taglist': map(typeset_tag, duplicates)})
        messages.append(t.render(c))
        return None
    tags = [(tag, True) for tag in primary_tags]
    tags.extend([(tag, False) for tag in other_tags])
    return tags

def prepare_body(body, messages):
    return body.strip()

SHORT_NAME_CHARS = '23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'

def make_short_name(length):
    return get_random_string(length, SHORT_NAME_CHARS)

test_body = """
First paragraf
is started here

We have
$$
\sum_{k=1}^n k
$$

and then we get the
result.

"""

def typeset_body_paragraph(par):
    par = par.replace('\n', ' ')
    par = re.sub(r'\s{2,}', ' ', par)
    par = par.strip()
    parts = par.split('$')
    for k in range(len(parts)):
        if k % 2 == 1:
            parts[k] = '\(' + parts[k].strip() + '\)'
    return '<p>' + ''.join(parts) + '</p>'

def typeset_body(body):
    parts = body.strip().split('$$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\n\[\n' + parts[i].strip() + '\n\]\n'
        else:
            parts2 = re.split(r'\s*\n\s*\n\s*', parts[i].strip())
            parts2 = map(typeset_body_paragraph, parts2)
            parts[i] = '\n'.join(parts2)
    return ''.join(parts)

def typeset_body2(st):
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
    return make_html_safe(''.join(parts))

