import re

def clean_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    return name

def normalize_tag(name):
    return clean_tag(name).lower()

