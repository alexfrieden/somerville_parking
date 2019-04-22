import pandas as pd
import os
from sodapy import Socrata

# Fetch from data.somervillema.gov if more recent data are available
# https://data.somervillema.gov/resource/97j2-xc5y.json
# See https://github.com/xmunoz/sodapy/blob/master/examples/basic_queries.ipynb

# Setup ----
socrata_domain = 'data.somervillema.gov'
socrata_dataset_identifier = '97j2-xc5y'
socrata_token = os.environ.get("SODAPY_APPTOKEN") # No token required here

inputname = 'City_of_Somerville_Parking_Permits.csv'
outputname = 'results.csv'

# Fetch metadata ----
# Manually specify which column to inspect for length, here looking at 'issued'

client = Socrata(socrata_domain, socrata_token)
metadata = client.get_metadata(socrata_dataset_identifier)
meta_issued = [x for x in metadata['columns'] if x['name'] == 'issued'][0]
nrow_available = meta_issued['cachedContents']['not_null']

# Does the required input file exist at all? If not, fetch it and write out csv
if os.path.isfile(inputname) == 'False':
    print('Getting data from ' + socrata_domain)
    results = client.get(socrata_dataset_identifier)
    df = pd.DataFrame.from_dict(results)
    df.to_csv(inputname, header=True)

# If it does exist, check to make sure it has the same number of rows as currently available.
# If not, fetch fresh data from scratch
if os.path.isfile(inputname):
    df = pd.read_csv(inputname)
    nrow_current = df.shape[0]
    if int(nrow_current) != int(nrow_available):
        print('Fresher data was found, updating from ' + socrata_domain)
        results = client.get(socrata_dataset_identifier)
        df = pd.DataFrame.from_dict(results)
        df.to_csv(inputname, header=True)


# Clean up fields -- seems there is trailing white space in half the Residential fields
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

# Make a list of residential units which have multiple parking permits
address_count = df[(df.type_name == 'Residential')].groupby(['st_addr', 'unit_num']).size().sort_values(ascending=False).head(100)

address_count.to_csv(outputname, header=True)

# Same, but now split by year
df.issued = pd.to_datetime(df.issued) # Super slow right now...
df['year_issued'] = df.issued.dt.year

address_count = df[(df.type_name == 'Residential')].groupby(['year_issued', 'st_addr', 'unit_num']).size().sort_values(ascending=False).head(100)

address_count.to_csv('results_by_year.csv', header=True)

