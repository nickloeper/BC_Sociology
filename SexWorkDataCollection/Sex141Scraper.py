
# coding: utf-8

# In[389]:

from bs4 import BeautifulSoup as bs
import requests as rq
import pandas as pd
import glob
import re


# ### DataFrame Setup

# In[428]:

df_columns = ['FORUM TITLE', 'THREAD TITLE', 'THREAD AUTHOR', 'REPLIES', 'VIEWS', 'URL', 'METADATA', 'DATE', 'BODY']
all_thread_info = []
def create_dataframe(): return pd.DataFrame(all_thread_info, columns = df_columns)


# ### Load/Parse HTML Files

# In[431]:

html_files = glob.glob('eforum/*.html')

def fetch_thread_html(thread_url):
    try:
        return get_bs_object(rq.get(thread_url).text)
    except requests.exceptions.RequestException as e:
        print (e)
        
def get_bs_object(html): return bs(html, 'lxml')

def open_html_file(file_name): return open(file_name)


# ### Helper Functions

# In[334]:

def strip_newlines(string): return string.replace('\n', '')


# ### BeautifulSoup Parsing

# In[424]:

def extract_thread_urls(thread): return thread.findAll('a')[0]['href']
def get_thread_tables(soup_html): return soup_html.find('form').findAll('table')
def get_thread_row_columns(row): return row.findAll('td')
def find_thread_table_partition(thread_tables):
    for i in range(len(thread_tables)):
        thread_cat_partitions = thread_tables[i].find('tr', {'class': 'category'})
        if thread_cat_partitions != None:
            if len(thread_cat_partitions.findAll(text='Threads')) > 0:
                return i
def extract_thread_table_info(thread_table):
    thread_url = thread_table.find('td', {'class': 'f_title'}).a['href'] or ''
    title = strip_newlines(thread_table.find('td', {'class': 'f_title'}).text) or ''
    author = thread_table.find('td', {'class': 'f_author'}).text.split('\n')[1] or ''
    views_and_replies = strip_newlines(thread_table.find('td', {'class': 'f_views'}).text) or ''
    replies, views = views_and_replies.split('/')
    return [title, author, replies, views, thread_url]
def get_forum_title(html): return html.find('tr', {'class': 'header'}).tr.td.text
def extract_user_info(thread_html):
    user_info = thread_html.find('td', {'class': 't_user'})
    if user_info == None:
        return ''
    else:
        metadata = user_info.find('div', {'class': 'smalltxt'}).text
        return metadata
def extract_post_date(thread_html):
    date_col = thread_html.find('table', {'class': 't_msg'})
    if date_col == None:
        return ''
    else:
        return strip_newlines(str(date_col.tr.td.div.findAll('div')[1].next)[9:])
def extract_post_body(thread_html):
    body = thread_html.find('table', {'class': 't_msg'})
    if body == None:
        return ''
    else:
        return body.findAll('div')[5].text       


# ### Main

# In[429]:

count = 0
for html_file in html_files:
    html_page = get_bs_object(open_html_file(html_file))
    forum_title = get_forum_title(html_page)
    thread_tables = get_thread_tables(html_page)
    partition = find_thread_table_partition(thread_tables)
    filtered_thread_tables = thread_tables[partition:]
    for thread_table in filtered_thread_tables:
        thread_info = extract_thread_table_info(thread_table)
        thread_html = fetch_thread_html(thread_info[-1])
        thread_info.append(extract_user_info(thread_html))
        thread_info.append(extract_post_date(thread_html))
        thread_info.append(extract_post_body(thread_html))
        all_thread_info.append([forum_title] + thread_info)
    count += 1
    print (count, '/', len(html_files), 'DONE')
df = create_dataframe()


# In[430]:

df.to_csv('Sex141ThreadData.csv')

