#!/usr/bin/env python3

import json

with open('../../stats.json', 'r') as f:
    data = json.load(f)

for family in sorted(data['unit']):
    for unit in sorted(data['unit'][family]):
        text = family + ':' + unit + ":"
        width = 43 - len(text)
        print(text + ' ' * width)
