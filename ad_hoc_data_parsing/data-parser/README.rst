###############################
Data Parser Tool
###############################

********
Overview
********
This tool parses .csv sample listing data to determine availablity or unique values of a specified column

Setup:
 1. Clone the repo
 2. Install packages

    pipenv install
    pipenv shell

********
Options:
********
#Display availability of a specified field 
  python3 data_parser.py <PATH TO CSV> -a -field <FIELD NAME>   
********
#List all unique results for a field
  python3 data_parser.py <PATH TO CSV> -lf -field <FIELD NAME>  
********
#List all field names and their availability 
#(Dont pass in any fields or argument flags)
  python3 data_parser.py <PATH TO CSV>
********
#Compare up to 4 columns of csv, returns only uniqe columns
#(Select distinct combinations of columns)
  python3 data_parser.py <PATH TO CSV> -c -field <FIELD NAME> -field2 <FIELD NAME> -field3 <FIELD NAME>
********


********
Example Usages:
********
$ python3 data_parser.py ../metadatas/maris/PropertyRinc.csv -a -field PropertySubType
Is available for 100.0% of samples

********
$ python3 data_parser.py ../metadatas/maris/PropertyRinc.csv -lf -field PropertySubType
Duplex
Multi-Family 2-4

********
$ python3 data_parser.py ../metadatas/maris/PropertyResi.csv -c -field Cooling -field PropertySubType -field PropertyType

                                         Cooling          PropertySubType PropertyType
0                                       Electric              Condominium  Residential
1                                       Electric                      NaN  Residential
4                                       Electric                    Villa  Residential
7                              Central Air,Zoned  Single Family Residence  Residential
9                                    Central Air  Single Family Residence  Residential
13                                         Other  Single Family Residence  Residential
14                                   Central Air                      NaN  Residential

