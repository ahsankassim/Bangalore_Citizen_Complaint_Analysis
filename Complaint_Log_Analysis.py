# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# %%
#helper_1
def num_validity_check(series):
    invalid_cols_count = pd.to_numeric(series, errors='coerce').isna().sum()
    return f'invalid_{series.name} : {invalid_cols_count}'

#helper_2
def range_check(series):
    return f'{series.min()}-{series.max()}'

#helper_3
def cross_fill(df , missing, source):
    miss = df[(df[missing].isna()) & (df[source].notna())][source].unique()
    for x in miss:
        y = df[(df[source] == x) & (df[missing].notna())][missing].iloc[0]
        df.loc[(df[source] == x ) & (df[missing].isna()), missing] = y 

# %%
df_original = pd.read_csv(r'data\blr_city_complain_log_2019_2022.csv', encoding="cp1252")
df = df_original.copy()

# %%
df.head(50)

# %% [markdown]
# ## **Data Cleaning**

# %%
df.columns

# %%
df['title'].sample(frac=1)

# %%
# Data Quality Check

df.columns = df.columns.str.strip().str.lower()
print('length:', len(df))
print('duplicates:',df.duplicated().sum())
print('---------------------------')
print('missing_values:''\n',df.isna().sum())
print()
print('missing and invalids''\n''-------------------------')
print('invalid_datetime:', pd.to_datetime(df['created_at'], errors='coerce').isna().sum())
print(num_validity_check(df['ward_id']))
print(num_validity_check(df['civic_agency_id']))
print(num_validity_check(df['ward_id']))
print(num_validity_check(df['sub_category_id']))

# %% [markdown]
# > Here, there is no complaint Id and hence can't track the duplicates, hence I'm going to try combinations to find the primary key before deciding what to do with the duplicates.

# %%
df[['created_at','category_id','complaint_status_title','ward_id','title','description','location','latitude',\
    'comment_count']].duplicated().sum()

# %% [markdown]
# > after several attempts, this is what I came close to and looking at this, it doesn't seem like genuine mistakes  made by citizens but rather system level glitch hence we are dropping it.
# 

# %%
df = df.drop_duplicates(keep= 'first').reset_index(drop= True)

# %%
df[pd.to_datetime(df['created_at'], errors='coerce').isna()]['created_at']


# %%
df['created_at'] = df['created_at'].str.replace('/', '-') 
df['created_at'] = pd.to_datetime(df['created_at'])

# %%
df[df['civic_agency_id'].isna()].sample(frac=1)

# %%
x = ['civic_agency_title','comment_count','complaint_status_title']
for i in x:
    print(df[df['civic_agency_id'].isna()][i].value_counts(),'\n')

# %%
print(df[(df['civic_agency_id'].isna()) & (df['complaint_status_title'] == 'Resolved')]['ward_title'].value_counts())
print('----------------------------------------')
print(df[(df['civic_agency_id'].isna()) & (df['complaint_status_title'] == 'Resolved')]['comment_count'].value_counts())
print('----------------------------------------')
print(df[(df['civic_agency_id'].isna()) & (df['complaint_status_title'] == 'Resolved')]['category_title'].value_counts())

# %%
df['ward_title'].value_counts()

# %% [markdown]
# > Majority of the complaints for which no civic agency is assigned are still open and a few (28) got resolved, and since the volumes are small, categories are relatively common and all of them have at least one follow up comment post the complaint. I'm concluding that these are solved through local contacts of the public.

# %%
cross_fill(df=df, missing='civic_agency_title', source= 'civic_agency_id')

# %%
df['civic_agency_title'] = df['civic_agency_title'].fillna('Not Assigned')
df['civic_agency_id'] = df['civic_agency_id'].fillna(-1)

# %%
df[df['address'].isna()].sample(frac=1)

# %%
df['address'] = df['address'].fillna('Not Provided')

# %%
cross_fill(df=df, missing= 'ward_title', source='ward_id')

# %%
range_check(df['ward_id'])

# %% [markdown]
# > The real data obtained for validity check is larger than range in this dataset, hence validity check for this column is avoided

# %%
df['sub_category_title'].value_counts()


# %%
print(df[(df['category_title'].isna()) & (df['category_id'].isna())]['sub_category_title'].value_counts())
print('----------------------------------')
print(df[(df['category_title'].isna()) & (df['category_id'].isna())]['sub_category_id'].value_counts())

# %%
print(df[(df['category_title'].isna()) & (df['category_id'].isna())]['sub_category_id'].count())

# %% [markdown]
# > So it is the same as category_id problem, the system failed to assign them properly or was removed due to some error in the filing process

# %%
cross_fill(df=df, missing='sub_category_title' , source= 'sub_category_id')

# %%
cross_fill(df=df, missing='category_id' , source= 'sub_category_id')

# %%
cross_fill(df=df, missing='category_title' , source= 'category_id')

# %%
# Data Quality Check Post Cleanup

df.columns = df.columns.str.strip().str.lower()
print('length:', len(df))
print('duplicates:',df.duplicated().sum())
print('---------------------------')
print('missing_values:''\n',df.isna().sum())
print()
print('missing and invalids''\n''-------------------------')
print('invalid_datetime:', pd.to_datetime(df['created_at'], errors='coerce').isna().sum())
print(range_check(df['created_at']))
print(num_validity_check(df['ward_id']))
print(num_validity_check(df['civic_agency_id']))
print(num_validity_check(df['category_id']))
print(num_validity_check(df['sub_category_id']))

# %%
df.dtypes


# %% [markdown]
# **Data Correction: Civic Agency Title Standardisation**
# 
# Duplicate civic agency entries were identified during analysis. Abbreviated and full-form titles representing the same agency were being treated as separate entities. Titles were standardised to a single consistent form at the cleaning stage before metric calculations.

# %%
df.loc[df['civic_agency_id'] == 10,'civic_agency_title'] = 'BBMP'
df.loc[df['civic_agency_id'] == 1,'civic_agency_title'] = 'BESCOM'
df.loc[df['civic_agency_id'] == 5,'civic_agency_title'] = 'BTC'
df.loc[df['civic_agency_id'] == 7,'civic_agency_title'] = 'KSPCB'
df.loc[df['civic_agency_id'] == 2,'civic_agency_title'] = 'BWSSB'

# %% [markdown]
# > checking for duplicates in other ID columns, which I should have done earlier.

# %%
cat_check = df.groupby(['category_id','category_title']).size().reset_index()
sub_cat_check = df.groupby(['sub_category_id','sub_category_title']).size().reset_index()
ward_check = df.groupby(['ward_id','ward_title']).size().reset_index()

# %%
print(cat_check[cat_check['category_id'].duplicated()])

# %%
print(df[df['category_id'] == 15]['category_title'].unique())
print(df[df['category_id'] == 470]['category_title'].unique())

# %%
df.loc[df['category_id'] == 15, 'category_title'] = 'Mobility - Roads, Footpaths and Infrastructure'
df.loc[df['category_id'] == 470, 'category_title'] = 'Street lighting'

# %%
#verification
cat_check = df.groupby(['category_id','category_title']).size().reset_index()
print(cat_check['category_id'].duplicated().sum())


# %%
print(sub_cat_check[sub_cat_check['sub_category_id'].duplicated()]['sub_category_id'])

# %%
temp = sub_cat_check[sub_cat_check['sub_category_id'].duplicated()]['sub_category_id']
for t in temp:
    print(t, df[df['sub_category_id'] == t]['sub_category_title'].unique())

# %%
df.loc[df['sub_category_id'] == 42, 'sub_category_title'] = 'Others'
df.loc[df['sub_category_id'] == 149, 'sub_category_title'] = 'Other Certificates'
df.loc[df['sub_category_id'] == 200, 'sub_category_title'] = 'Wrong Parking'
df.loc[df['sub_category_id'] == 311, 'sub_category_title'] = 'Sewerage and Storm Water Blockages and Overflows'
df.loc[df['sub_category_id'] == 511, 'sub_category_title'] = 'Stray Dog Sterlisation and Birth Control'
df.loc[df['sub_category_id'] == 709, 'sub_category_title'] = 'Public Urination or Yellow Spots'
df.loc[df['sub_category_id'] == 715, 'sub_category_title'] = 'Require Public Toilet or Playing and Gym Equipment'

# %%
df.loc[df['sub_category_id'].isin([710,711]), 'sub_category_id'] = 710
df.loc[df['sub_category_id'].isin([712,713,714]), 'sub_category_id'] = 711
df.loc[df['sub_category_id'] == 710, 'sub_category_title'] = 'Dirty or Unusable Public Toilet'
df.loc[df['sub_category_id'] == 711, 'sub_category_title'] = 'Footpath Broken or Blocked by Debris'

# %% [markdown]
# > Sub categories that were different but had same underlying explainations were merged and then corrected.

# %%
#verification
sub_cat_check = df.groupby(['sub_category_id','sub_category_title']).size().reset_index()
print(sub_cat_check[sub_cat_check['sub_category_id'].duplicated()]['sub_category_id'])

# %%
print(ward_check['ward_id'].duplicated().sum())

# %% [markdown]
# **Labeling Mismatch**
# 
# Some complaints with missing agencies which was earlier labelled as Not Assigned has category titles that are already existing that could potentially be used to cross fill, which was overlooked while cleaning. They are fixed here before metric calculations.

# %%
df[df['civic_agency_title'] == 'Not Assigned']['category_title'].value_counts()

# %% [markdown]
# > The labels "Not Assigned" and "-1" are going to be reversed, then the rows with existing categories will be cross filled and then the remaining will be again filled with the former labels.

# %%
df['civic_agency_id'] = df['civic_agency_id'].replace(-1, np.nan)
df['civic_agency_title'] = df['civic_agency_title'].replace("Not Assigned", np.nan)

# %%
df[df['category_title'] == "PWD"]

# %% [markdown]
# > so apparently there are certain categories (like "PWD" for example) for whom there is no civic agency title or id present at all for all the complaints under that, so the cross fill helper function kept running into IndexError, so I'm going to write the code manually here with an empty check before cross filling. 

# %%
missing_id = df[(df['civic_agency_id'].isna()) & (df['category_title'].notna())]['category_title'].unique()
for x in missing_id:
    if df[(df['category_title'] == x) & (df['civic_agency_id'].notna())]['civic_agency_id'].empty:
        continue
    y = df[(df['category_title'] == x) & (df['civic_agency_id'].notna())]['civic_agency_id'].iloc[0]
    df.loc[(df['category_title'] == x) & (df['civic_agency_id'].isna()), 'civic_agency_id'] = y


# %%
cross_fill(df=df, missing='civic_agency_title', source='civic_agency_id')

# %%
df[df['civic_agency_id'].isna()]['category_title'].value_counts()

# %%
df[df['category_title'] == 'Roads and Footpaths'][['sub_category_id','sub_category_title']].value_counts()

# %%
df[df['category_title'] == 'Mobility - Roads, Footpaths and Infrastructure']['sub_category_title'].value_counts()

# %% [markdown]
# > The category called Road and Footpaths suprisingly have no civic agency assigned despite similar complaint categories being present under `Mobility - Roads, Footpaths and Infrastructure` category.
# >  Upon investigation the `Roads and Footpaths` category has only one sub category (`Build new footpaths and repair broken footpaths`), and under `Mobility - Roads, Footpaths and Infrastructure` there are sub categories construction and repair of footpaths.
# > It is assumed as labeling bug by the system and this sub category will be merged with `Mobility - Roads, Footpaths and Infrastructure` category.

# %%
df[df['category_title'] == 'Mobility - Roads, Footpaths and Infrastructure']['category_id'].unique()

# %%
df.loc[df['sub_category_title'] == 'Build new footpaths and repair broken footpaths', ['category_id','category_title']] = \
     15.0, 'Mobility - Roads, Footpaths and Infrastructure'

# %%
df.loc[df['category_title'] == 'Mobility - Roads, Footpaths and Infrastructure', 'civic_agency_title'] = 'BBMP'

# %%
cross_fill(df=df, missing='civic_agency_id', source='civic_agency_title')

# %%
#Verification
df[df['civic_agency_title'].isna()]['category_title'].value_counts()

# %%
#verification
df['category_title'].value_counts()

# %%
df['civic_agency_title'] = df['civic_agency_title'].fillna('Not Assigned')
df['civic_agency_id'] = df['civic_agency_id'].fillna(-1)

# %%
df_clean = df.copy()

# %%
# df_clean.to_csv(r'data\blr_city_complain_log_analysis(cleaned).csv')

# %% [markdown]
# **______________________________________________________________________________________________________________________________________________________________________________**

# %% [markdown]
# ## **EDA**

# %% [markdown]
# #### **Date-Based Analysis**

# %%
df['complaint_month'] = df['created_at'].dt.month_name()
df['complaint_year'] = df['created_at'].dt.year

# %%
date_stats = pd.DataFrame()
date_stats['year'] = df['complaint_year']
date_stats['month'] = df['complaint_month']
date_stats['day'] = df['created_at'].dt.day_name()
date_stats['year_month'] = date_stats['year'].astype(str) + ' ' + date_stats['month'].str[:3]

# %%
date_stats['year_month'].value_counts()[:15]

# %%
#AI generated
plot_df=date_stats.groupby(['year','month']).size().reset_index(name='row_count')

month_order=['January','February','March','April','May','June','July','August','September','October','November','December']

plot_df['month']=pd.Categorical(plot_df['month'],categories=month_order,ordered=True)
plot_df=plot_df.sort_values(['year','month'])
plot_df['label']=plot_df['month'].astype(str)

colors=plt.cm.Blues((plot_df['row_count']-plot_df['row_count'].min())/(plot_df['row_count'].max()-plot_df['row_count'].min()))

plt.figure(figsize=(15,5))
plt.bar(range(len(plot_df)),plot_df['row_count'],color=colors)
plt.xticks(range(len(plot_df)),plot_df['label'],rotation=90)
plt.ylabel('Row Count')
plt.xlabel('Month')
plt.title('Row Count by Year and Month')
for _,group in plot_df.groupby('year'):
    plt.axvline(group.index.max()+0.5,color='lightgray',linewidth=1)
plt.tight_layout()
plt.show()

# %%
print(date_stats['year'].value_counts())
print(date_stats['year'].value_counts(normalize=True).round(4)*100)

# %%
print(date_stats['month'].value_counts(),'\n')
print(date_stats['month'].value_counts(normalize=True).round(4)*100, '\n')

# %%
df[df['category_title'] == 'Covid 19'][['complaint_month','complaint_year']].sort_values(by='complaint_year',ascending=True).reset_index(drop=True)

# %%
df[df['category_title'] == 'Covid 19']['created_at'].count()

# %% [markdown]
# #### **Date Analysis Insights**
# NOTE : External data about events happened in the period concerned has been obtained from external sources to look up possible connections to the highs and lows present in the data.
# 
# 2019 has the highest number of complaints registered with 7371 complaints (45.96%) while 2022 being the lowest with 1550 complaints (9.66%), partly because the dataset only captures upto july 2022.
# 
# Elevated complaint levels from January 2019 to March 2020 coincided with the 2019 Lok Sabha Elections, Karnataka's political crisis and government transition, Anti CAA/NRC protests, and the emergence of COVID 19. These events likely increased civic activity, public gatherings, traffic disruptions, and citizen interaction with public authorities.
# 
# The exceptionally high complaint volumes recorded in October 2019 (865) and November 2019 (797) may also be associated with the post-government-transition period and political developments surrounding the cancellation of state-sponsored Tipu Jayanti celebrations.
# 
# The elevated complaint volume observed in December 2020 (740) coincided with the then ongoing COVID 19 restrictions, economic disruptions, and BBMP administrator-led governance. These factors may have contributed to increased civic and administrative grievances.
# 
# The decline of complaint volume in 2020 may partially be associated with citizen reluctance to engage with authorities during COVID 19 restrictions, beyond just reduced civic activity.
# 

# %% [markdown]
# **______________________________________________________________________________________________________________________________________________________________________________**

# %% [markdown]
# #### **ward-Based Analysis**

# %% [markdown]
# **Assumption: Open Complaint Status**  
# Complaints recorded with a status of `Open` represent complaints pending acknowledgement at the time of data extraction. In the absence of a dataset cutoff date, no inference is drawn regarding whether these complaints were deliberately delayed, subsequently addressed or remain permanently unacknowledged. Hence, they are considerd in aggregate metrics since they are ultimately a part of the system, but will not be a subject of standalone ward analysis going forward.

# %% [markdown]
# **On-The_job Complaint Status** : 
# Similarly complaints recorded with a status of `On-The-Job` are not going to be a subject of stand alone analysis going forward as meaningful interpretation requires a time factor defining the complaint flow which is unavailable in this dataset.

# %% [markdown]
# **Closed Complaint Status**
# Complaints with a status of `Closed` were included alongside Rejected complaints when calculating the Complaint Ignorance Rate. For this analysis, The share of complaints marked Rejected or Closed, treated in this analysis as ignored. This is a simplifying assumption, as complaints may also be closed or rejected for legitimate reasons, such as insufficient information, triviality, or infeasibility of the requested action.

# %%
df['complaint_status_title'].value_counts(normalize=True)*100

# %%
#ward performance metrics
ward = df.groupby(['ward_title', 'ward_id'])

ward_stats = ward.agg(complaint_count=('created_at', 'count')).reset_index()

complaint_status = df.groupby(['ward_title','ward_id','complaint_status_title']).size().unstack(fill_value=0).reset_index()
ward_stats = pd.merge(ward_stats,complaint_status, on=['ward_title','ward_id'], how='left')

comments = ward['comment_count'].sum().reset_index(name='total_comments')
ward_stats = pd.merge(ward_stats, comments, how='left', on=['ward_title','ward_id'])

ward_stats.columns = ward_stats.columns.str.replace('-', '_').str.lower()

# %%
ward_stats['complaint_acceptance_rate'] =\
    ward_stats[['resolved', 'on_the_job','rejected','closed','re_opened']].sum(axis=1)/\
    ward_stats['complaint_count']
ward_stats['complaint_resolution_rate'] = ward_stats['resolved']/ward_stats['complaint_count']
ward_stats['complaint_ignorance_rate'] = ward_stats[['rejected','closed']].sum(axis=1)/ward_stats['complaint_count']
ward_stats['complaint_re_opening_rate'] = ward_stats['re_opened']/ward_stats['complaint_count']
ward_stats['comments_per_complaint'] = (ward_stats['total_comments'] / ward_stats['complaint_count']).round(2)
ward_stats['effective_resolution_rate'] = ward_stats['complaint_resolution_rate'] / ward_stats['complaint_acceptance_rate']

# %%
ward_stats_org = ward_stats[ward_stats.columns[:10]]
ward_stats = ward_stats.drop(columns=ward_stats.columns[3:10])

# %%
ward_stats

# %% [markdown]
# #### ward Performance
# Builds `ward_stats` with acceptance, resolution, effective resolution, ignorance, re-opening rates and comments per complaint for each ward.
# `ward_stats_org` retains the raw status counts for reference.

# %%
cols = ['complaint_count','complaint_acceptance_rate','complaint_resolution_rate','complaint_ignorance_rate','complaint_re_opening_rate','comments_per_complaint', 'effective_resolution_rate']

# %%
print(ward_stats['complaint_count'].describe())

# %% [markdown]
# > wards cannot be judged with metrics calculated above without their population or area data, since it is unavailable in this dataset, I'm considering wards with more than 100 registered complaints.
# >
# > **Reasoning**: wards with higher areas or population would naturally receive more complaints than small ones, and comparing their performances without normalizing for either of the factors mentioned earlier would be simply unfair.

# %%
complaints = ward_stats['complaint_count']
ward_stats[complaints>100].describe()

# %%
for x in cols:
    y = ward_stats[complaints.ge(100)][x].median()
    print(f'{x}: {y}')

# %% [markdown]
# > Exploring to see if a cohort analysis based on complaint count creates meaningful differentiation.

# %%
ward_stats[complaints.lt(50)].describe()

# %%
ward_stats[(complaints.ge(50) & (complaints.le(100)))].describe()

# %%
ward_stats[(complaints.gt(100) & (complaints.le(300)))].describe()

# %%
ward_stats[complaints.gt(300)].describe()

# %% [markdown]
# > My earlier justification for excluding wards with fewer than 100 complaint counts was not supported by the data, which revealed only marginal metric differences for all four cohorts. Hence all wards are included in the analysis going forward.
# > But still wards with fewer than 100 complaint could be susceptible to small sample bias, small sample sizes produce uneven metric values that are not comparable in fair grounds. While cohort-level analysis revealed only marginal differences, individual ward comparisons remain susceptible to statistical instability.

# %%
ward_stats[complaints >= 100].sort_values(by='complaint_resolution_rate', ascending=False).head(10)

# %%
ward_stats.sort_values(by='complaint_resolution_rate', ascending=False).head(10)

# %% [markdown]
# >Looking at the above data, Gurappanpalya with 82% resolution rate with only 29 complaints and Padarayanapura with 50% resolution rate with only 2 complaints is disproportionately higher, which confirms that wards with lower complaint volume are susceptible to small sample bias. Hence moving forward only wards with more than 100 complaints will be considered.

# %%
ward_stats[complaints >= 100].sort_values(by='complaint_acceptance_rate', ascending=False).head(10)

# %%
ward_stats[complaints >= 100].sort_values(by='effective_resolution_rate', ascending=True).head(10)

# %%
ward_stats[complaints >= 100].sort_values(by='complaint_ignorance_rate', ascending=True).head(10)

# %%
ward_stats[complaints >= 100].sort_values(by='complaint_re_opening_rate', ascending=True).head(10)

# %%
ward_stats[complaints >= 100].sort_values(by='complaint_count', ascending=False).head(10)

# %%
# a helper function to pick out the ward titles by the respective sorting order
def ward_stat_picker(column_name, ascending=False, force = 10):
    if ascending:
        daf = ward_stats[ward_stats['complaint_count']>100].sort_values(by= column_name, ascending=True).head(force)
        duf = list(daf['ward_title'])    
        return duf
    else:
        daf = ward_stats[ward_stats['complaint_count']>100].sort_values(by= column_name, ascending=False).head(force)
        duf = list(daf['ward_title'])    
        return duf

# %%
# a helper to pick out the most common wards to figure out performance of the wards.
def top_10(positive_cols, negative_cols, mode='best'):
    if mode == 'best':
        empty = []
        for i in positive_cols:
            empty.extend(ward_stat_picker(i))
        for i in negative_cols:
            empty.extend(ward_stat_picker(i, ascending=True))
        from collections import Counter

        count = Counter(empty)
        best_10 = []
        for ward, appearances in count.most_common():
            best_10.append(f"{ward}: {appearances}")
        return best_10

    if mode == 'worst':
        empty = []
        for i in positive_cols:
            empty.extend(ward_stat_picker(i, ascending=True))
        for i in negative_cols:
            empty.extend(ward_stat_picker(i))
        from collections import Counter

        count = Counter(empty)
        worst_10 = []
        for ward, appearances in count.most_common():
            worst_10.append(f"{ward}: {appearances}")
        return worst_10

# %%
pos_cols = ['complaint_count', 'complaint_acceptance_rate','complaint_resolution_rate','effective_resolution_rate']
neg_cols = ['complaint_ignorance_rate','complaint_re_opening_rate','comments_per_complaint']

# %%
top_10(positive_cols=pos_cols, negative_cols=neg_cols, mode='best')

# %%
top_10(positive_cols=pos_cols, negative_cols=neg_cols, mode='worst')

# %%
df[df['ward_title'] == 'C V Raman Nagar']

# %%
ward_stats[complaints >= 100].sort_values(by='comments_per_complaint', ascending=True).head(10)

# %%
print(ward_stats[complaints >= 100]['comments_per_complaint'].skew())
print(ward_stats[complaints >= 100]['comments_per_complaint'].median())

# %%
print(ward_stats[(complaints >= 100) & (ward_stats['comments_per_complaint'] >= 1.2)][cols].mean())
print('-------------------------------------------------')
print(ward_stats[(complaints >= 100) & (ward_stats['comments_per_complaint'] < 1.2)][cols].mean())

# %% [markdown]
# > Exploring to see if complaints created in certain periods are more likely to get re-opened.

# %%
df['is_reopened'] = (df['complaint_status_title'] == 'Re-opened').astype(int)

# %%
df[df['is_reopened'] == 1][['complaint_month','complaint_year']].value_counts(normalize=True)

# %%
df[(df['is_reopened'] == 1) & (df['ward_title'] == 'C V Raman Nagar')][['complaint_month','complaint_year']].value_counts(normalize=True)

# %% [markdown]
# > February, March and June of 2019 have the most of complaints re-opened, but nothing could be found to explain the spike.
# > The spike in re-opened complaints in june 2019 in `Sir C V Raman Nagar` could be likely due to the world environmental day awareness program hosted there.

# %% [markdown]
# > Exploring to see if any ward has complaints concentrated in any particular agency.

# %%
ge_100 = list(ward_stats[ward_stats['complaint_count'].ge(100)]['ward_title'])


ward_agency_dist = df[df['ward_title'].isin(ge_100)]\
    .groupby('ward_title')['civic_agency_title'].value_counts(normalize=True).unstack(fill_value=0)\
    .map(lambda x: round((x*100), 2))


ward_agency_dist.skew()

# %%
ward_agency_dist.median()

# %%
ward_agency_dist

# %% [markdown]
# > Exploring to see the wards and their peak complaint periods.

# %%
ward_period_dist = df[df['ward_title'].isin(ge_100)]\
    .groupby(['complaint_year','complaint_month'])['ward_title']\
    .value_counts().rename('complaint_count').reset_index()


ward_period_dist['total'] = ward_period_dist.groupby('ward_title')['complaint_count'].transform('sum')
ward_period_dist['complaint/period'] = ward_period_dist['complaint_count'] / ward_period_dist['total']

max_vals = ward_period_dist.groupby('ward_title')['complaint/period'].transform('max')

max_comp_per_ward = ward_period_dist[ward_period_dist['complaint/period'] == max_vals]

# %%
max_comp_per_ward['complaint/period'].quantile(0.9)

# %%
max_comp_per_ward[max_comp_per_ward['complaint/period'].ge(0.1299)].sort_values(by='complaint/period', ascending=False)

# %%
ward_stats.to_csv(r'data/ward_stats.csv')

# %% [markdown]
# #### **ward-Based Analysis Insights**
# `Bellanduru` with the highest complaint resolution rate (44.42%), second highest complaint acceptance rate(57.5%) and the most no. of complaints received (727) has displayed elite efficiency in grievance redressal and civic engagement.
# 
# `Hagadur` has an acceptance of 43.88% and yet has an ignorance rate of 2.95% which is two times the median value, and also below average in other metrics (resolution rate: 23.63% and effective resolution: 53.85%) indicates a consistent and clear underperformance.
# 
# `Atturu, Gottigere, Horamavu, Hemmigepura, Agrahara, Kodigehalli` have zero ignorance rate despite receiving more than 100 complaints on average and specifically `Horamavu` has exhibited an excellent complain handling process with 506 complaints received.
# 
# `Sampangiram Nagar` with the lowest acceptance rate (24.86%) and resolution rate (16.38) has yet to acknowledge most of its complaints.
# 
# `Sir C V Raman Nagar` leads in complaint re opeining rate with 7.48% compared to the average of 2.4%.
# 
# As Bengaluru's primary municipal body, BBMP's ward-level dominance is expected, accounting for over 70% of all complaints in every relevant ward except two. No other agency exceeds this threshold in any ward
# 
# Complaint categories with more than 1.2 comments per complaint exhibit higher acceptance (49.53% versus 41.21%) and resolution rates (33.12% versus 27.47%). However, similar effective resolution rates (~67% )among acknowledged complaints suggest that comment activity may be associated with complaint engagement rather than directly influencing final resolution outcomes.
# 
# Ward-level concentration by category was also considered, but since Mobility - Roads, Footpaths and Infrastructure dominates complaint volume city-wide, this would likely just reflect the category's overall dominance rather than any ward-specific pattern, similar to the redundancy noted for agency-level concentration. Not pursued further
# **______________________________________________________________________________________________________________________________________________________________________________________**
# 
# out of six wards that showed unusual high complaint concentration (>13%, 90th percentile) within a single month:
# 
# - `Bilekahalli, Sampangiram Nagar and Hoysala Nagar` (concentrated in Dec 2020) consistent with the spike in citywide complaint levels likely due to covid restrictions and BBMP administrator-led governance
# - `Vasanth Nagar` with higher complaints in Oct 2019 also coincided with post-government transition period explained above (see Date Analysis Insights).
# - `Kodegahalli` with their complaints clustered in March 2020 could be linked to the broader period of political instability and civic disruption, which are explained above (see Date Analysis Insights).
# - `Sir C V Raman Nagar` held a city wide World Environment day in June 2019 event which could be responsible for the higher concentration and higher re-open rate.

# %% [markdown]
# **______________________________________________________________________________________________________________________________________________________________________________**

# %% [markdown]
# #### **Agency-Based Analysis**

# %% [markdown]
# **Note:** Same status assumptions from the ward Analysis section apply here.

# %%
# Agency Performance Metrics

agency = df.groupby(['civic_agency_title', 'civic_agency_id'])

agency_stats = agency.agg(complaint_count=('created_at', 'count')).reset_index()

complaint_status_agency = df.groupby(['civic_agency_title', 'civic_agency_id', 'complaint_status_title']).size()\
    .unstack(fill_value=0).reset_index()
agency_stats = pd.merge(agency_stats, complaint_status_agency, on=['civic_agency_title', 'civic_agency_id'], how='left')

comments = agency['comment_count'].sum().reset_index(name='total_comments')
agency_stats = pd.merge(agency_stats, comments, how='left', on=['civic_agency_title','civic_agency_id'])

agency_stats.columns = agency_stats.columns.str.replace('-', '_').str.lower()

# %%
agency_stats['complaint_acceptance_rate'] = \
    agency_stats[['resolved', 'on_the_job', 'rejected', 'closed', 're_opened']].sum(axis=1)/\
    agency_stats['complaint_count'] 
agency_stats['complaint_resolution_rate'] = agency_stats['resolved'] / agency_stats['complaint_count'] 
agency_stats['complaint_ignorance_rate'] = agency_stats[['rejected', 'closed']].sum(axis=1) / agency_stats['complaint_count'] 
agency_stats['complaint_re_opening_rate'] = agency_stats['re_opened'] / agency_stats['complaint_count'] 
agency_stats['comments_per_complaint'] = (agency_stats['total_comments'] / agency_stats['complaint_count'])
agency_stats['effective_resolution_rate'] = agency_stats['complaint_resolution_rate'] / agency_stats['complaint_acceptance_rate']

# %%
agency_stats_org = agency_stats[agency_stats.columns[:10]]
agency_stats = agency_stats.drop(columns=agency_stats.columns[3:10])
agency_stats = agency_stats.rename(columns={'civic_agency_id' : 'agency_id', 'civic_agency_title' : 'agency_title'})

# %% [markdown]
# #### Agency Performance
# Builds `agency_stats` with acceptance, resolution, effective resolution, ignorance, re-opening rates and comments per complaint for each agency.
# `agency_stats_org` retains the raw status counts for reference.

# %%
agency_stats_org

# %%
agency_stats.sort_values(by='complaint_resolution_rate', ascending=False)

# %% [markdown]
# > Only agencies with more than 100 complaint counts will be considered moving forward, since agencies with lower complaint volumes carry small sample bias which can elevate values disproportionately as demonstrated in ward analysis.

# %%
cols = ['complaint_count','complaint_acceptance_rate','complaint_resolution_rate','complaint_ignorance_rate','complaint_re_opening_rate','comments_per_complaint']
agency = agency_stats['complaint_count']
for x in cols:
    y = agency_stats[agency.ge(100)][x].mean()
    print(f'{x}: {y}')

# %%
ge100_agency = agency_stats[agency_stats['complaint_count'].ge(100)]['agency_title']

agency_period_dist = df[df['civic_agency_title'].isin(ge100_agency)]\
    .groupby(['complaint_year','complaint_month'])['civic_agency_title']\
    .value_counts().rename('complaint_count').reset_index()


agency_period_dist['total'] = agency_period_dist.groupby('civic_agency_title')['complaint_count'].transform('sum')
agency_period_dist['complaint/period'] = agency_period_dist['complaint_count'] / agency_period_dist['total']

max_vals = agency_period_dist.groupby('civic_agency_title')['complaint/period'].transform('max')

max_comp_per_agency = agency_period_dist[agency_period_dist['complaint/period'] == max_vals]

max_comp_per_agency

# %%
agency_stats[agency.ge(100)].sort_values(by='complaint_resolution_rate', ascending=False)

# %%
df.groupby('civic_agency_title')['category_title'].value_counts()

# %% [markdown]
# #### **Agency-Based Analysis Insights**
# Among agencies receiving more than 100 complaints, only `BBMP` and `BTC` demonstrated statistically comparable performance, as more than ~85% of complaints assigned to the remaining agencies remained unacknowledged. `BBMP` recorded an acceptance rate of 50.40%, a resolution rate of 35.41% and an effective resolution rate of 70.25%, while `BTC` recorded a resolution rate of 19.27%, an effective resolution rate of 36% and a higher ignorance rate of 3.34%.
# 
# `BBMP's` dominance is expected. As the primary municipal body, it covers the broadest range of complaint categories and receives the highest complaint volume, yet maintained a 70% effective resolution rate despite operating at a significantly larger scale than any other agency in the dataset. In contrast, `BTC` has an effective resolution rate of 36% and ignorance rate of 33%, on further analysis of categories and sub categories, it is revealed that `BTC` has only one category under it and `BTC's` lower resolution, effective resolution and higher ignorance rates are driven by parking related sub category whose intrinsic nature provides a plausible explaination for its lower resolution and higher ignorance rates, which is detailed below.

# %% [markdown]
# **_____________________________________________________________________________________________________________________________________________________________________________________________________________**

# %% [markdown]
# #### **Category-Based Analysis**

# %% [markdown]
# **Note:** Same status assumptions from the category Analysis section apply here.

# %%
# Category performance metrics
category = df.groupby(['category_title', 'category_id'])

category_stats = category.agg(complaint_count=('created_at', 'count')).reset_index()

complaint_status = df.groupby(['category_title','category_id','complaint_status_title']).size().unstack(fill_value=0).reset_index()
category_stats = pd.merge(category_stats, complaint_status, on=['category_title','category_id'], how='left')

comments = category['comment_count'].sum().reset_index(name='total_comments')
category_stats = pd.merge(category_stats, comments, how='left', on=['category_title','category_id'])

category_stats.columns = category_stats.columns.str.replace('-', '_').str.lower()

# %%
category_stats['complaint_acceptance_rate'] =\
    category_stats[['resolved', 'on_the_job','rejected','closed','re_opened']].sum(axis=1)/\
    category_stats['complaint_count']
category_stats['complaint_resolution_rate'] = category_stats['resolved']/category_stats['complaint_count']
category_stats['complaint_ignorance_rate'] = category_stats[['rejected','closed']].sum(axis=1)/category_stats['complaint_count']
category_stats['complaint_re_opening_rate'] = category_stats['re_opened']/category_stats['complaint_count']
category_stats['comments_per_complaint'] = (category_stats['total_comments'] / category_stats['complaint_count']).round(2)
category_stats['effective_resolution_rate'] = category_stats['complaint_resolution_rate'] / category_stats['complaint_acceptance_rate']

# %%
category_stats_org = category_stats[category_stats.columns[:10]]
category_stats = category_stats.drop(columns=category_stats.columns[3:10])

# %%
cols = ['complaint_count','complaint_acceptance_rate','complaint_resolution_rate','complaint_ignorance_rate','complaint_re_opening_rate','comments_per_complaint']
category = category_stats['complaint_count']

for x in cols:
    y = category_stats[category.ge(100)][x].mean()
    print(f'{x}: {y}')

# %% [markdown]
# #### Category Metrics
# Builds `category_stats` with acceptance, resolution, effective resolution, ignorance, re-opening rates and comments per complaint for each agency.
# `category_stats_org` retains the raw status counts for reference.

# %%
category_stats

# %% [markdown]
# > Only categories with more than 100 complaint counts will be considered moving forward, since categories with lower complaint volumes carry small sample bias which can elevate values disproportionately as demonstrated earlier in ward analysis.

# %%
category_stats[category.ge(100)].sort_values(by='complaint_acceptance_rate', ascending=False)

# %% [markdown]
# Six of sixteen categories yellow spot, pollution, water supply and services, electricity and power supply, crime and safety, sewerage systems and others have recorded a complaint acceptance rate of less than 5%, meaning 95% of their complaints remain unacknowledged, Sewage systems category showed a marginally higher acceptance rate but still only around 10%. This mirrors a similar pattern observed at the agency level, whether these complaints were accepted, or otherwise cannot be determined with the available data.

# %%
category_stats[category.ge(100)].sort_values(by='complaint_resolution_rate', ascending=False)

# %%
category_stats[category.ge(100)].sort_values(by='complaint_count', ascending=False)

# %%
category_stats[category.ge(100)].sort_values(by='effective_resolution_rate', ascending=True)

# %%
category_stats[category.ge(100)].sort_values(by='complaint_ignorance_rate', ascending=False)

# %%
category_stats[category.ge(100)].sort_values(by='comments_per_complaint', ascending=True)

# %%
category_stats_org[category_stats_org['category_title'] == 'Trees and Saplings']

# %% [markdown]
# > exploring to see the pattern if any between category and period of complaints registered.

# %%
ge100_category = category_stats[category_stats['complaint_count'].ge(100)]['category_title']

category_period_dist = df[df['category_title'].isin(ge100_category)]\
    .groupby(['complaint_year','complaint_month'])['category_title']\
    .value_counts().rename('complaint_count').reset_index()


category_period_dist['total'] = category_period_dist.groupby('category_title')['complaint_count'].transform('sum')
category_period_dist['complaint/period'] = category_period_dist['complaint_count'] / category_period_dist['total']

max_vals = category_period_dist.groupby('category_title')['complaint/period'].transform('max')

max_comp_per_category = category_period_dist[category_period_dist['complaint/period'] == max_vals]

# %%
category_period_dist

# %%
max_comp_per_category

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Street lighting']
monthly.groupby('complaint_month')['complaint_count'].mean().to_frame()

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Electricity and Power Supply']
monthly.groupby('complaint_month')['complaint_count'].mean()  

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Water Supply and Services']
monthly.groupby('complaint_month')['complaint_count'].mean()

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Parks & Recreation']
monthly.groupby('complaint_month')['complaint_count'].mean()  

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Sewerage Systems']
monthly.groupby('complaint_month')['complaint_count'].mean()  

# %%
monthly = category_period_dist[category_period_dist['category_title'] == 'Storm Water Drains']
monthly.groupby('complaint_month')['complaint_count'].mean()  

# %%
max_comp_per_category.sort_values(by='category_title')

# %%
df[df['category_title']=='Roads and Footpaths']['created_at'].sort_values().min()

# %%
df[df['category_title']=='Yellow Spot']['created_at'].sort_values().min()

# %% [markdown]
# #### **Category-Based Analysis Insights**
# 
# - `Garbage and Unsanitary Practices` is the category with the highest resolution rate (49.83%), an impressive effective resolution rate (84.37%) and with 3933 complaints. It has also has the highest comments per complaint meaning complaints gets resolved but only after some back and forth. Could improve resolving complaints at the first instance.
# - Although complaint handling metrics are moderate,` Mobility - Roads, Footpaths and Infrastructure` represents the largest operational burden, with about 5,183 complaints. Consequently, improvements in resolution efficiency could have a significant citywide impact.
# - `Trees and saplings` have surprisingly good metrics for an environmental category with 40.38% acceptance rate, 30.77% resolution rate, 76.19% effective resolution rate, 0% ignorance rate and with 1.07 comments per complaint. suggesting that once complaints were acknowledged, they are being solved without much follow ups.
# - `Street lighting` category has zero ignorance rate and a 44.53% resolution rate and a 82.14% effective resolution rate despite having 1498 complaints registered, suggesting street lighting problems are taken seriously even at large scale.
# - `Traffic and Road Safety` is the sole category under BTC, it exhibits the weakest complaint handling performance among high volume categories. Despite more than half of complaints being acknowledged (53.56%), only 19.31% were resolved (effective resolution of 36.05%) while 33.44% fell into the ignored category, however the sub category analysis indicates that BTC's (or this category's) lower resolution rate and higher ignorance rate is driven by two parking related sub categories whose intrinsic nature provides a plausible explaination, which is detailed below in the sub category analysis.
# - only about 24 of 121 of `Parks & Recreation` category complaints were ever acknowledged, and of those, 14 were on the job at the time of extraction. Among the 10 that reached a final outcome, 8 were resolved and 2 were reopened, so the category's weak point is it's low acceptance.
# 
# _________________________________________________________________________________________________________________________________________________________________________________________
# 
# - Three of the categories have a clear break in terms of complaint clustering in a single month. Out of them,
#     - `Roads and Footpaths` and `Yellow Spot` will be ignored, since the earliest complaint date recorded for both the categories are 22nd Feb 2022 and 8th Dec 2020 respectively fall within or near their apparent concentration period, indicating that their high concentration is due to limited category history and not genuine complaint clustering.
#     - March 2022 was around the time when the covid restrictions around the city eased up and people started using public parks after a while, and also this is when BBMP finalized its budget for 22-23 setting aside 92.3 crores for `Parks and Recreation`, these could be the plausible causes for the spike in march 2022.
#     - A civic protest movement around this period was also considered, but complaint volume in the associated ward did not show a corresponding increase, so it was ruled out.
# _________________________________________________________________________________________________________________________________________________________________________________________
# - Month level complaint concentration is only investigated for categories that could likely present seasonal patterns. Parks & Recreation is the only exception which is investigated since it surfaced as a temporal anamoly in "maximum complaints per category per period" analysis
# 
#     - `Street lighting` complaints exhibits clear monsoon seasonality (September peak: 46 avg vs. April post monsoon: 20.75), yet maintain an 82.14% effective resolution rate and zero ignorance rate. Suggesting consistent handling across seasonal demands.    
#     - May 2019 thunderstorm and regular rain patterns of Bangalore explains the spike for `Electricity and Power Supply` in May (10%), the November spike has no clear seasonal or external explanation and is noted as unexplained
#     - The cluster of complaints in March (16.75%) and February (11%) for `Water Supply and Services` exhibites a clear seasonal pattern, peaking during February and March. This coincides with Bengaluru's pre-monsoon period, when groundwater levels begin declining and water demand starts increasing due to rising temperatures.
#     - `Parks and Recreation` category also has spikes in March (11%) and February (9.5%), increased civilian usage citing the pleasant weather, civic agencies rushing maintenence before the end of FY and other causes listed above could likely be the causes.
#     - `Sewerage Systems` category has also demonstrated a spike in March (12.25%), but it does not represent a seasonal pattern and hence noted as unexplained.
#     - `Storm Water Drains` category has even distribution of complaints in all months.

# %% [markdown]
# #### **Sub Category level Analysis**

# %% [markdown]
# Categories were split into two groups based on resolution rate for sub category-level investigation. Categories below 20% resolution rate (including Traffic and Road Safety, separately flagged for its high 33.44% ignorance rate) are examined to identify whether a single sub category disproportionately drags down category-level performance. Categories above 20% resolution rate are examined to check whether strong performance is broad-based across subcategories or concentrated in a few. Categories with near-zero acceptance rates (identified in the category-based analysis) are excluded, as the lack of acknowledged complaints does not provide meaningful basis for sub category comparison.

# %%
cat_gt20 = ['Storm Water Drains','Trees and Saplings','Mobility - Roads, Footpaths and Infrastructure','Animal Husbandry','Street lighting','Garbage and Unsanitary Practices']
cat_lt20 = ['Traffic and Road Safety','Community Infrastructure and Services']
selected_cats = ['Storm Water Drains','Trees and Saplings','Mobility - Roads, Footpaths and Infrastructure','Animal Husbandry',\
    'Street lighting','Garbage and Unsanitary Practices','Traffic and Road Safety','Community Infrastructure and Services']

# %%
#sub_category performance metrics
sub_category = df[df['category_title'].isin(selected_cats)].groupby(['category_title','sub_category_title', 'sub_category_id'])

sub_category_stats = sub_category.agg(complaint_count=('created_at', 'count')).reset_index()

complaint_status = df.groupby(['sub_category_title','sub_category_id','complaint_status_title']).size().unstack(fill_value=0).reset_index()
sub_category_stats = pd.merge(sub_category_stats,complaint_status, on=['sub_category_title','sub_category_id'], how='left')

comments = df[df['category_title'].isin(selected_cats)].groupby(['sub_category_title', 'sub_category_id'])\
    ['comment_count'].sum().reset_index(name='total_comments')
sub_category_stats = pd.merge(sub_category_stats, comments, how='left', on=['sub_category_title','sub_category_id'])

sub_category_stats.columns = sub_category_stats.columns.str.replace('-', '_').str.lower()

# %%
sub_category_stats['complaint_acceptance_rate'] =\
    sub_category_stats[['resolved', 'on_the_job','rejected','closed','re_opened']].sum(axis=1)/\
    sub_category_stats['complaint_count']
sub_category_stats['complaint_resolution_rate'] = sub_category_stats['resolved']/sub_category_stats['complaint_count']
sub_category_stats['complaint_ignorance_rate'] = sub_category_stats[['rejected','closed']].sum(axis=1)/sub_category_stats['complaint_count']
sub_category_stats['complaint_re_opening_rate'] = sub_category_stats['re_opened']/sub_category_stats['complaint_count']
sub_category_stats['comments_per_complaint'] = (sub_category_stats['total_comments'] / sub_category_stats['complaint_count']).round(2)
sub_category_stats['effective_resolution_rate'] = sub_category_stats['complaint_resolution_rate'] / sub_category_stats['complaint_acceptance_rate']

# %%
sub_category_stats

# %%
sub_category_stats[sub_category_stats['complaint_count'].ge(30)].groupby('category_title').size()

# %%
sub_category_stats_org = sub_category_stats[sub_category_stats.columns[:11]]
sub_category_stats = sub_category_stats.drop(columns=sub_category_stats.columns[4:11])

# %%
print('gt20 categories')
for cat in cat_gt20:
    g = sub_category_stats[(sub_category_stats['category_title'] == cat) & (sub_category_stats['complaint_count'] >= 30)]['complaint_count']
    print(f'cv of {cat} : {g.std()/g.mean()}')
print('------------------------------------------------------')
print('lt20 categories')
for cat in cat_lt20:
    g = sub_category_stats[(sub_category_stats['category_title'] == cat) & (sub_category_stats['complaint_count'] >= 30)]['complaint_count']
    print(f'cv of {cat} : {g.std()/g.mean()}')

# %% [markdown]
# > For subcategory analysis, the complaint count threshold is lowered to 30, a '>100' cutoff (as used for categorys) would exclude nearly all subcategories given their uneven spread (CV > 0.5 for most categories), leaving too little to compare. 

# %%
sub_category_stats[sub_category_stats['category_title'] == 'Parks & Recreation']

# %%
# small helper to inspect the sub categories with ease.
def inspect(category):
    return sub_category_stats[(sub_category_stats['category_title'] == category) & (sub_category_stats['complaint_count'] >= 30)]\
        .sort_values(by=['complaint_resolution_rate', 'complaint_acceptance_rate'], ascending=[False, False])

# %%
inspect('Community Infrastructure and Services')

# %% [markdown]
# #### **Insights from Sub Category level Analysis**
# 
# > **NOTE** : the ≥30 total filter is necessary but not sufficient — any individual rate is still sanity-checked against its own accepted count before being reported, rather than assumed safe just because it cleared the total threshold.
# 
# - ***Garbage and Unsanitary Practices*** category has only one subcategory `Clearance Of Garbage Dump Or Black Spot` pulling most of the weight with 3100 complaints registered to it out of 3933 complaints, which is also confirmed by the cv of 1.89, and that sub category also has a CPC of 2.07 and resolution rate of 55.32% which explains the category leading in both the metrics.
#     - Complaints regarding new garbage units `'Build Garbage/Waste Composting Units' sub category` are solved effectively once acknowledged, as evidenced by an effective resolution rate of 75% (9/12).
# - As indicated by a cv of 1.38 in ***street lighting*** category, `Maintenance/Repair Of Streetlight` sub category is the hero with 1292/1498 complaints under it, with an 84% effective resolution rate. Moreover it's worth mentioning that none of the sub categories under this has ignored any complaints which is also emphasized in the category level insights.
# - With only two meaningful sub categories under ***Animal Husbandry*** and with one sub category registered with 770/801 complaints, it is indeed carried by one single sub category which defines most of its performance.
# - ***In Mobility - Roads, Footpaths and Infrastructure category***, two(`Tarring Or Asphalting Of Existing Road` and `Fixing/Reparing Potholes`) out of 11 of its sub categories are registered with 3863 complaints, which explains a cv of 1.72. However the two sub categories having the highest acceptance rates (69.65% and 62.1% respectively) has the lowest effective resolution rates (50.84% & 55.83%) than its other sub catgories which generally sits between 62-70%.
# - ***Trees and saplings*** have only one meaningful sub category.
# - ***Storm Water Drains*** has two meaningful sub categories with relatively fair spread of complaints (90 & 42).
# - The sub categories of ***Traffic and Road Safety*** category has a fair spread of complaints among them consistent with the cv of 0.48.
#     - Only the `Riding Without A Helmet` sub category has a standout effective resolution rate of 70.73% with an acceptance rate of 82.55% while others average around 20% (effective resolution rate) which translates to 36% overall effective resolution rate.
#     - Two of the sub categories (`Wrong Parking` and `Parking On Footpath`) have standout ignorance rates (50.44% & 60.4%) and resolution rates (17.6% and 16.83%) with an acceptance rate of 70.8% and 78.22% which leads to the 19.31% and 33.44% of category level resolution rate and ignorance rate. But Complaints related to wrong parking and parking on footpaths often rely on sufficient evidence, such as clear photographs, timestamps, or identifiable vehicle details, for enforcement action. Where evidence is incomplete or inconclusive, authorities may be unable to verify the violation, particularly if the vehicle is no longer present for physical verification. This reliance on verifiable evidence, combined with the time-sensitive nature of these violations, may contribute to comparatively higher ignorance rates or lower resolution rates in these categories. 
# 
# - ***Community Infrastructure and Services*** category has only two meaningful sub categories with a fair spread (cv = 0.16) out of which one has a 72.73% effective resolution rate but only shares 44% of complaints while the other has only 15% of effective resolution rate which defines the overall effective resolution rate of 40%.

# %% [markdown]
# #### **Finding: Association Between Complaint Tone and Resolution Outcomes**

# %% [markdown]
# **Assumption: Keyword-Based Sentiment Tagging**
# Complaints were tagged as "Urgent" or "Frustrated" based on the presence of predefined keywords in the description field. A single complaint could be tagged under both categories. This is a coarse proxy for sentiment/tone and does not account for context, sarcasm, or phrasing not captured by the keyword list. It is not a validated sentiment classification.

# %% [markdown]
# <!-- #### **Complaint Language Analysis using keywords** -->

# %%
urgent_words = [
    'dangerous','danger', 'unsafe', 'broken', 'accident', 'fall', 'electrocution',
    'sewage', 'stagnant', 'open drain', 'fire', 'collapse', 'crack',
    'urgent', 'immediately', 'serious', 'hazard', 'risk', 'injury',
    'children','disease','disorder','hurt','seriously'
]


frustration_words = [
    'again', 'repeated', 'multiple times', 'many times','no action', 'no response','ignored',
    'still not', 'tired of', 'everyday', 'daily', 'recurring', '2 days', 'two days','3 days','4 days','one week',
    'same','no water'
]

df['is_urgent'] = df['title'].str.lower().str.contains('|'.join(urgent_words)) | \
    df['description'].str.lower().str.contains('|'.join(urgent_words))

df['is_frustrated'] = df['title'].str.lower().str.contains('|'.join(frustration_words)) | \
    df['description'].str.lower().str.contains('|'.join(frustration_words))


# %%
urgency_stats = df.groupby('is_urgent')['complaint_status_title'].value_counts().unstack(fill_value=0).reset_index()
urgency_stats.columns = urgency_stats.columns.str.replace('-','_').str.lower()
urgency_stats['total'] = urgency_stats.sum(axis=1, numeric_only=True)
urgency_stats['resolution_rate'] = urgency_stats['resolved']/urgency_stats['total']
urgency_stats['effective_resolution_rate'] = urgency_stats['resolved'] / (urgency_stats['total'] - urgency_stats['open'])
urgency_stats

# %%
frustrated_stats = df.groupby('is_frustrated')['complaint_status_title'].value_counts().unstack(fill_value=0).reset_index()
frustrated_stats.columns = frustrated_stats.columns.str.replace('-','_').str.lower()
frustrated_stats['total'] = frustrated_stats.sum(axis=1, numeric_only=True)
frustrated_stats['resolution_rate'] = frustrated_stats['resolved']/frustrated_stats['total']
frustrated_stats['effective_resolution_rate'] = frustrated_stats['resolved'] / (frustrated_stats['total'] - frustrated_stats['open'])
frustrated_stats

# %%
complaint_type_stats = df.groupby(['is_urgent','is_frustrated'])['complaint_status_title'].value_counts().unstack(fill_value=0).reset_index()
complaint_type_stats.columns = complaint_type_stats.columns.str.replace('-','_').str.lower()
complaint_type_stats['total'] = complaint_type_stats.sum(axis=1, numeric_only=True)
complaint_type_stats['resolution_rate'] = complaint_type_stats['resolved']/complaint_type_stats['total']
complaint_type_stats['effective_resolution_rate'] = complaint_type_stats['resolved'] / (complaint_type_stats['total'] - complaint_type_stats['open'])
complaint_type_stats

# %% [markdown]
# **Finding: Urgency and Frustration Show Opposite Associations with Resolution**
# Complaints flagged as "Frustrated" showed a modestly higher resolution rate (33.10% vs. 30.23%) and effective resolution rate (70.5% vs. 67.5%) compared to non-frustrated complaints. Complaints flagged as "Urgent" showed the opposite, a slightly lower resolution rate (28.96% vs. 31.31%) and effective resolution rate (63.8% vs. 69.4%) than non-urgent complaints. This pattern held consistently across all four combinations of the two tags, suggesting the direction of each association is not an artifact of one tag overlapping with the other.
# 
# No causal claim is made. It is unclear whether frustration-coded language reflects complaints that were already further along the resolution process (and thus more likely to mention dissatisfaction with delay), or whether such language itself influences how complaints are handled.

# %% [markdown]
# 

# %%
# df.to_csv('data/blr_city_complain_log_2019_2022(processed).csv')


