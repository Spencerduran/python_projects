import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Parse sample data .csv to find unique values and availablity for a field')
parser.add_argument('path', type=str, help='Path to sample data .csv')
parser.add_argument('-field', action='append', type=str, help='Field from csv to analyze')
parser.add_argument('-a', action='store_true', help='availablitiy percent of a field')
parser.add_argument('-lf', action='store_true', help='list unique values')
parser.add_argument('-c', action='store_true', help='compare columns')

args = parser.parse_args()
df = pd.read_csv(args.path)

if args.lf:
        fieldValues = df[args.field].drop_duplicates().to_string(index=False)
        print (fieldValues)
elif args.a:
        availableRows = df[args.field].notnull().sum()
        availablity = availableRows / len(df) * 100
        print('Is available for ' + str(float(availablity)) + '% of samples')

elif args.c:
        columns = []
        for field in args.field:
            if field:
                columns.append(field)
            continue
        fieldValues = df[columns].drop_duplicates().to_string(index=False)
        print(fieldValues)

else:
    for column in df:
        columnValues = df[column]
        availableRows = columnValues.notnull().sum()
        invalidRows = sum(columnValues == '***')
        availability = (availableRows - invalidRows) / len(df) * 100
        print(column + ": " + str(availability) + "%")

