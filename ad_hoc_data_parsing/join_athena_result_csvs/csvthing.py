import pandas as pd

# Read .csv files
#df1 = pd.read_csv("/Users/spencerduran/Code_Repos/python_projects/ad_hoc_data_parsing/join_athena_result_csvs/csvs/POLICY_ACTIVE.csv")
#df2 = pd.read_csv("/Users/spencerduran/Code_Repos/python_projects/ad_hoc_data_parsing/join_athena_result_csvs/csvs/MEMBER_INSURED_COUNT.csv")

# Perform inner join on the two dataframes using PC_CONT as the join key
#result = pd.merge(df1, df2, on="PC_CONT", how="inner")

# Output required rows to a CSV file
#required_rows.to_csv('No_branch_data.csv', index=False)

# Read output CSV file into a pandas dataframe
df = pd.read_csv("/Users/spencerduran/Code_Repos/python_projects/ad_hoc_data_parsing/join_athena_result_csvs/No_branch_data.csv")

# Subset the dataframe based on specified values in the SA_LIFECAD_DESC_L01_x column
values_to_keep = ['Active', 'BasePaid-Up', 'ConservPend', 'FreeLookPer.', 'FullyPaid-Up', 'LapsePending', 'LatePayOffrPnd', 'Pay-Out', 'ReducedPaid-Up']
sa_lifecad_desc_l01_x_subset = df[df['SA_LIFECAD_DESC_L01_x'].isin(values_to_keep)]

# Subset the dataframe by unique values in the MEMBER_EMAIL_ADDRESS column
unique_email_subset = sa_lifecad_desc_l01_x_subset.drop_duplicates(subset=['MEMBER_EMAIL_ADDRESS'])

# Extract the specified fields from the resulting dataframe
result = unique_email_subset[['MEMBER_CLIENT_ID', 'MEMBER_EMAIL_ADDRESS', 'MEMBER_FIRST_NAME', 'MEMBER_LAST_NAME', 'PC_CONT']]

# Output the resulting dataframe to a CSV file
result.to_csv('output.csv', index=False)
