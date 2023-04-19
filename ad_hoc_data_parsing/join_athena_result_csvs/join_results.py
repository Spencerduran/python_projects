import argparse
import os
import pandas as pd

joined_data = pd.DataFrame(columns=['source_id'])
data = []
for file in os.scandir('./csvs'):
    if file.name.endswith('.csv'):
        filename = os.path.basename(file)[:-4]
        filepath = file.path
        if args.rename:
            df_renamed = pd.read_csv(filepath, index_col=0).rename({'count': filename}, axis='columns')
            data.append(df_renamed)
        if not args.rename:
            df_original = pd.read_csv(filepath, index_col=0)
            data.append(df_original)

for frame in (data):
    joined_data = pd.merge(joined_data, frame, on=['source_id'], how='outer')
print(joined_data)
joined_data.to_csv(r'./results.csv', index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser( description='join together athena result csvs')
    parser.add_argument( '-rename', action='store_true', help= 'Use this flag to rename the "count" column to the filename')
    args = parser.parse_args()
    main()
