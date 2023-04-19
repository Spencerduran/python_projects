import argparse
import json

def split_file():
    with open('Alip_dictionary_full.md') as f:
        f_out = None
        for line in f:
            if line.startswith('**T_'):      # we need a new output file
                title = line
                if f_out:
                    f_out.close()
                f_out = open(f'{title[2:-3]}.txt', 'w')
            if f_out:
                f_out.write(line)
        if f_out:
            f_out.close()

def extract_tables(): 
    total_list = []
    with open ('/Users/spencerduran/tools/file_splitter/ALIP_Schema.json') as f:
        data = json.load(f)
        for table in data:
            for key, value in table.items():
                if key == 'Schema':
                    schema_name = value 
                if key == 'Table Name':
                    table_name = value
            addition = f"{schema_name}.{table_name}"
            print(addition)

def main():
    extract_tables()

if __name__ == "__main__":
    main()
