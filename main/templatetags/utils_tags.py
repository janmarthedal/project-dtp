from django import template
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

register = template.Library()

class IncludeRawNode(template.Node):
    def __init__(self, filepath):
        self.filepath = filepath

    def render(self, context):
        filepath = self.filepath.resolve(context)
        filepath = settings.PROJECT_BASE + 'templates/' + filepath
        try:
            with open(filepath, 'r') as fp:
                output = fp.read()
        except IOError:
            if settings.DEBUG:
                return 'include_raw %s failed' % filepath
            else:
                return ''
        return output

@register.tag
def include_raw(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    filepath = parser.compile_filter(filename)
    return IncludeRawNode(filepath)
    
