from urllib import request
import xml.etree.ElementTree as ET
from datetime import datetime

feed = request.urlopen('http://blog.teoremer.com/rss.xml').read()
root = ET.fromstring(feed)
channel = root.find('channel')

result = []

def parse_date(st):
    time = datetime.strptime(st[:-6], '%a, %d %b %Y %H:%M:%S')
    #time -= timedelta(hours = int(st[-5:]) / 100)
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
