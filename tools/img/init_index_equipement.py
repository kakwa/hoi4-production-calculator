#!/usr/bin/env python3

import json

with open('../../stats.json', 'r') as f:
    data = json.load(f)

for year in sorted(data['equipement']):
    for equipement in sorted(data['equipement'][year]):
        text = year + '.' + equipement + ":"
        width = 43 - len(text)
        print(year + '.' + equipement + ":" + ' ' * width)
