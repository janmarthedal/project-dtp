import re

def clean_tag(name):
    name = name.strip()
    name = re.sub(r' {2,}', r' ', name)
    return name

# assumes 'name' has been cleaned
def normalize_tag(name):
    return name.lower()

