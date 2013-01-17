import string
import random

SHORT_NAME_CHARS = '23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
#SHORT_NAME_CHARS = ''.join(set(string.ascii_letters + string.digits) - set('0oO1lI'))

def make_short_name(length):
    return ''.join(random.choice(SHORT_NAME_CHARS) for _ in xrange(length))

