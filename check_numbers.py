import yaml
import pprint

with open('legislators-historical.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

with open('legislators-current.yaml', 'r') as f:
    data2 = yaml.load(f, Loader=yaml.FullLoader)

data = data + data2

yrs = [str(i) for i in range(1901, 2020, 2)]

output = {}
for y in yrs:
    i = 0
    for leg in data:
        for tm in leg['terms']:
            if tm['start'].startswith(y):
                i = i + 1
    output[y] = i
    print(y, output[y])

pprint.pprint(output)
