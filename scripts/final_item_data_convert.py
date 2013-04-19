import json
from items.models import final_id_to_name

f = open('items/fixtures/initial_data.json', 'r')
st = f.read()

data = json.loads(st)

for elem in data:
    if elem['model'] == 'items.finalitem':
        elem['fields']['final_id'] = final_id_to_name(elem['pk'])

st = json.dumps(data)

f = open('items/fixtures/initial_data2.json', 'w')
f.write(st)

