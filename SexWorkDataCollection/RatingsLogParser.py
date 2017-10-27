
# coding: utf-8

# In[1]:

from bs4 import BeautifulSoup as bs
import pandas as pd


# ### Load Dataframe

# In[6]:

filename = 'Sex141ThreadData.csv'
df = pd.read_csv(filename)


# ### Create Dataframe

# In[68]:

df_columns = ['USER', 'DATE', 'TYPE', 'VALUE', 'COMMENT']
all_thread_info = []
def create_dataframe(): return pd.DataFrame(all_thread_info, columns = df_columns)


# ### Parse Ratings Log

# In[100]:

def get_bs_object(html): return bs(html, 'lxml')
def get_ratings_entries(ratings_log):
    parsed_entries = []
    if not pd.isnull(ratings_log):
        ratings_log_bs = get_bs_object(ratings_log)
        ratings_entries = ratings_log_bs.find_all('tr')
        if ratings_entries:
            for entry in ratings_entries:
                entry_values = [col.text.strip('\xa0') for col in entry.find_all('td')]
                parsed_entries.append(entry_values)
    return parsed_entries


# In[101]:

values_df = pd.DataFrame([], index=pd.MultiIndex(levels=[[], []], labels=[[], []]), columns = df_columns)
for i in range(len(df)):
    thread_id = df.loc[i, "URL"][50:55]
    ratings_entries = get_ratings_entries(df.loc[i, "RATINGS LOG"])
    for j in range(len(ratings_entries)):
        values_df.loc[(thread_id, j), :] = ratings_entries[j]


# In[107]:

values_df.to_csv('ThreadRatingLogs.csv')

