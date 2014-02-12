from urllib import request
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime

feed = request.urlopen('http://blog.teoremer.com/rss/').read()
root = ET.fromstring(feed)
channel = root.find('channel')

result = []

def parse_date(st):
    offset = int(st[-5:])
    delta = timedelta(hours = offset / 100)
    time = datetime.strptime(st[:-6], '%a, %d %b %Y %H:%M:%S')
    time -= delta
    return time.strftime('%Y-%m-%d')

for item in channel.findall('item'):
    result.append({
        'title': item.find('title').text,
        'link': item.find('link').text,
        'date': parse_date(item.find('pubDate').text),
        'description': item.find('description').text
    })

print('def get_blog_feed():')
print('    return ' + str(result))
print()
