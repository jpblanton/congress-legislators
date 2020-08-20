from dateutil.relativedelta import relativedelta
import yaml
import pandas as pd
import numpy as np


#  takes in a list of Term objects containing potentially a dozen fields
#  only needs a few 
def get_years(df):
    df2 = df.copy()
    big_lst = []
    df2['type'] = ''
    df2['party'] = ''
    for i, row in df2.iterrows():
        yrs_lst = []
        s, e, t, p = row['terms']
        s = pd.to_datetime(s)
        e = pd.to_datetime(e)
        n_years = e.year - s.year
        for j in range(n_years+1):
            dt = s+relativedelta(years=+j)
            if dt < e:
                yrs_lst.append(dt)
        df2.loc[i, 'type'] = t
        df2.loc[i, 'party'] = p
        big_lst.append(yrs_lst)
    df2['yrs'] = big_lst
    return df2.explode('yrs')


#  terms is sorted by oldest one first, so we can start with age at first inauguration
#  gonna need to look into discontinuous reps - otherwise will get credit for serving too much
#  look at using dict or something instead of static df for varying start & end dates - one for each term, so can calculate over discontinuous range
def convert_to_df(lst):
    records = []
    for leg in lst:
        cur = []
        if 'birthday' in leg['bio']:
            cur.append(leg['bio']['birthday'])
        else:
            cur.append('2020-01-01')
        if 'official_full' in leg['name']:
            cur.append(leg['name']['official_full'])
        else:
            cur.append(' '.join(leg['name'].values()))
        start = leg['terms'][0]['start']
        end = leg['terms'][-1]['end']
        # cur.append(start)
        # cur.append(end)
        tmp = []
        for t in leg['terms']:
            t_var = []
            t_var.append(t['start'])
            t_var.append(t['end'])
            t_var.append(t['type'])
            try:
                t_var.append(t['party'])
            except KeyError:
                t_var.append('None')
            tmp.append(tuple(t_var))
        cur.append(tuple(tmp))
        records.append(tuple(cur))
    cols = ['birth_date', 'full_name', 'terms']# 'start_date', 'end_date', 'terms']
    df = pd.DataFrame.from_records(records, columns=cols)
    df = df.apply(lambda x: pd.to_datetime(x) if x.name.find('date') > 0 else x)
    # df['age_at_start'] = df.apply(lambda x: relativedelta(x['start_date'], x['birth_date']), axis=1)
    # df['age_at_end'] = df.apply(lambda x: relativedelta(x['end_date'], x['birth_date']), axis=1)
    # df['interval'] = df.apply(lambda x: list(set(pd.date_range(x['start_date'], x['end_date']).year)), axis=1)
    return df

#  right away - we have the df. can explode to get a different row for each year in office for each person. Then can filter by year and that's relatively straightforward. But need to increase age each year when we explode
#  get rows where the start_date yr == "interval", then we can go thru line by line and increment on false and reset on true (very slow, but)


with open('legislators-historical.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

with open('legislators-current.yaml', 'r') as f:
    data2 = yaml.load(f, Loader=yaml.FullLoader)

data = data + data2
df = convert_to_df(data)
df = df.explode('terms')
df = get_years(df)
df['age'] = df['yrs'] - df['birth_date']
df = df.reset_index(drop=True)
df['year'] = df['yrs'].dt.year

#  relative delta (start/end date; birth date) can produce age in y/m/d
#  may have to be row-wise apply func
#  pd.timedelta(end_date, start_date) should give a dtIndex with every day during their term; that + .year + set() should give the years they were in office - can easily produce ages
#  dict w/ years as key, list of (rep, age) as the values

#  Legislator object including bday, name, and list of years in office (on Jan 20/Mar 4)
#  then can query the db of legislator objects and just filter for year we want
#  object probably also includes derived prop for avg age
