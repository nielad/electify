# merge_dataframes.py

import pandas as pd
df_2024 = pd.read_csv("/src/other_data/2024 demographic data.csv")
df_polls_2024 = pd.read_csv("/src/other_data/daily_state_polling_averages.csv")

df_polls_2024['state_year'] = df_polls_2024['state'] + '_2024'
df_polls_2024 = df_polls_2024[['state_year', 'dem_poll_advantage']]

df_2024 = pd.merge(df_polls_2024, df_2024, how = 'outer')
df_2024.dropna(inplace=True)
df_2024.to_csv("/src/other_data/presidential predict data 2024.csv", index = False)
print("merge dataframes complete!")