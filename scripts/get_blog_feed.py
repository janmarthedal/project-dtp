import urllib
import xml.etree.ElementTree as ET

feed = urllib.urlopen('http://blog.teoremer.com/feed').read()
root = ET.fromstring(feed)
channel = root.find('channel')

result = []

for item in channel.findall('item'):
    result.append({
                   'title':       item.find('title').text,
                   'link':        item.find('link').text,
                   'description': item.find('description').text
                   })

print 'def get_blog_feed():'
print '    return ' + str(result)
print ''
