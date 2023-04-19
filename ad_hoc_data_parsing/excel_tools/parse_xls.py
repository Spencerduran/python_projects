import pandas as pd

xls = pd.ExcelFile('./results.xls', index_col=0)
df1 = pd.read_excel(xls, 'values_missing_resi_farm_park')
df2 = pd.read_excel(xls, 'values_miss_res_farm_prk_lnd')

print(f"{df1}\n{df2}")
