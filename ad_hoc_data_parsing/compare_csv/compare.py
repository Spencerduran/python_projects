import pandas as pd
from csv_diff import compare, load_csv

files = ['./input1.csv', './input2.csv']

diff = compare(load_csv(open(files[0], encoding='utf-8-sig'), key="ListingKey"),
               load_csv(open(files[1], encoding='utf-8-sig'), key="ListingKey"))


final_frame = pd.DataFrame()
for changetype, vals in diff.items():
    if changetype == "changed":
        for change in vals:
            listingkey = change.get("key")
            changedfieldvalues = change.get("changes")
            for fieldname, values_changed in changedfieldvalues.items():
                value1 = values_changed[0]
                value2 = values_changed[1]
                changedict = {
                    #'Change Type': changetype,
                    'Changed Value': value2,
                    'Original Value': value1,
                    'ListingKey': listingkey,
                    'Field Name': fieldname
                }
            final_frame = final_frame.append(changedict, ignore_index=True)
final_frame = final_frame.reindex(columns = ['ListingKey','Field Name','Original Value','Changed Value'])
final_frame.to_csv(r'./output.csv', index = False, header = True)
print(final_frame)
#    if changetype == "added" or changetype == "removed":
#        print(vals)
#        changedict = {
#            'Change Type': changetype,
#        }
#    if changetype == "columns_added" or changetype == "columns_removed":
#        print(changetype)
#        changedict = {
#            'Change Type': changetype,
#        }
#        final_frame = final_frame.append(changedict, ignore_index=True)
