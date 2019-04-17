import pandas as pd
df = pd.read_csv('City_of_Somerville_Parking_Permits.csv')
address_count = df.groupby(['st_addr','unit_num']).size().sort_values(ascending=False).head(70)
print(address_count)
