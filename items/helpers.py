import re
import string
from django.template import Context
from django.utils.crypto import get_random_string
from django.utils.http import urlquote, urlencode
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
    return name

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

def typeset_body2(body):
    parts = body.strip().split('$$')
    for i in range(len(parts)):
        if i % 2 == 1:
            parts[i] = '\n\[\n' + parts[i].strip() + '\n\]\n'
        else:
            parts2 = re.split(r'\s*\n\s*\n\s*', parts[i].strip())
            parts2 = map(typeset_body_paragraph, parts2)
            parts[i] = '\n'.join(parts2)
    return ''.join(parts)

def conceptMatch(match, maths, secret):
    key = 'Z%s%iZ' % (secret, len(maths))
    maths.append((key, key))
    name = match.group(1) or match.group(2)
    # TODO: use reverse lookup
    url = '/concept/' + urlquote(match.group(2))
    if match.group(3):
        url += '?' + urlencode({ 'tags': match.group(3) })
    return '<a href="%s">%s</a>' % (url, name)

def typeset_body(st):
    secret = make_short_name(8)
    parts = st.split('$$')
    maths = []
    for i in range(len(parts)):
        if i % 2 == 1:
            key = 'Z%s%iZ' % (secret, len(maths))
            maths.append((key, '\[' + parts[i] + '\]'))
            parts[i] = key
        else:
            parts2 = parts[i].split('$')
            for j in range(len(parts2)):
                if j % 2 == 1:
                    key = 'Z%s%iZ' % (secret, len(maths))
                    maths.append((key, '\(' + parts2[j] + '\)'))
                    parts2[j] = key
            parts[i] = ''.join(parts2)
    st = ''.join(parts)
    st = re.sub(r'\[([a-zA-Z ]*)#([a-zA-Z ]+)(?:\(([a-zA-Z ]+(?:,[a-zA-Z ]+)*)\))?\]',
                lambda match: conceptMatch(match, maths, secret), st)
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

