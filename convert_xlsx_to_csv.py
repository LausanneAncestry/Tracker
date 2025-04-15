import pandas as pd
import os

for file in os.listdir("all_census"):
    print(f"Converting {file}")
    try:
        data_xls = pd.read_excel(f'all_census/{file}', 'Sheet1', index_col=None)
        data_xls.to_csv(f'all_census/{file[:-5]}.csv', encoding='utf-8', sep=";")
    except:
        print("This file is already a csv")