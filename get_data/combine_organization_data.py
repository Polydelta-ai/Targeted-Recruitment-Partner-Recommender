import pandas as pd

first_df = pd.read_csv('data/AK_organization_data.csv')
remainder_df = pd.read_csv('data/WY_organization_data.csv')

final_df = pd.concat([first_df, remainder_df])

final_df.to_csv('data/organization_data.csv', index=False)