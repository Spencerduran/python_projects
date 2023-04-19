import argparse
import json
import pandas as pd

parser = argparse.ArgumentParser(description='Convert json data from postman to csv of listings')
parser.add_argument('path', type=str, help='Path to input sample data .json')
parser.add_argument('name', type=str, help='Name for output listing data')

args = parser.parse_args()
json_data = args.path
outputName = args.name

f = open(json_data)
data = json.load(f)
f.close()

df = pd.json_normalize(data['value']) 
df.to_csv(outputName + '.csv', sep=',', index = False)
