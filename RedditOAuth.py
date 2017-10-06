
# coding: utf-8

# In[2]:

import requests
import requests.auth as auth
import pandas as pd
import matplotlib as plt
import seaborn
import numpy as np
import praw
import calendar
import datetime


# ### Client Credentials

# In[3]:

client_ID = '7GX6Snu8X4G0mw'
client_secret = 'tfth7RHsDy4l7_3p8k4-ya5Wgo0'
username = 'nick_loeper'
password = 'Yoyomama111996!'
auth_headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}


# ### Token retreival 

# In[4]:

def auth_obj(client_ID, client_secret):
    return auth.HTTPBasicAuth(client_ID, client_secret)


# In[5]:

def auth_post_data(username, password):
    return {"grant_type": "password", "username": username, "password": password}


# In[6]:

def get_access_token(client_auth, post_data, auth_headers):
    response_json = requests.post("https://www.reddit.com/api/v1/access_token", 
                                  auth=client_auth, 
                                  data=post_data, 
                                  headers=auth_headers).json()
    return response_json['access_token']


# In[7]:

client_auth = auth_obj(client_ID, client_secret)
post_data = auth_post_data(username, password)
token = get_access_token(client_auth, post_data, auth_headers)
token
headers = {"Authorization": "bearer " + str(token), "User-Agent": "ChangeMeClient/0.1 by YourUsername"}


# # Requests for data

# ### Listing and Comment Fields

# In[94]:

submission_fields = ['id', 'author', 'title', 'selftext', 'score', 'created_utc', 'url']
comment_fields = ['submission_id', 'id', 'author', 'body', 'created_utc', 'score', 'ups', 'downs']
reddit = praw.Reddit(client_id=client_ID,
                     client_secret=client_secret,
                     user_agent="ChangeMeClient/0.1 by YourUsername")
dark_net_sub = reddit.subreddit('DarkNetMarkets')
silk_road_sub = reddit.subreddit('SilkRoad')


# ### Requests

# In[8]:

def get_submissions(start, end, subr):
    return [reddit.submission(id=submission) for submission in subr.submissions(start, end)]


# In[122]:

def get_submission_comments(sub_id):
    submission = reddit.submission(sub_id)
    return submission.comments.list()


# In[199]:

def get_all_comments(submissions):
    comments = []
    count = 1
    num_rows = len(submissions['id'])
    for submission_id in submissions['id']:
        sub_comments = get_submission_comments(submission_id)
        comments.append(extract_comment_data(sub_comments, submission_id))
        print (count, " / ", num_rows)
        count += 1
    all_comments = pd.concat(comments)
    all_comments.reset_index(inplace=True, drop=True)
    return all_comments


# In[10]:

def get_month_utc_range(number_of_month, year):
    num_of_days = calendar.monthrange(year, number_of_month)[1]
    first_day_utc = (datetime.datetime(year, number_of_month, 1) - datetime.datetime(1970, 1, 1)).total_seconds()
    last_day_utc = (datetime.datetime(year, number_of_month, num_of_days) - datetime.datetime(1970, 1, 1)).total_seconds() + 86400.0 
    print (first_day_utc, last_day_utc)
    return (first_day_utc, last_day_utc)


# In[20]:

def get_yearly_submissions(year, subr):
    num_of_months = 12
    monthly_submissions = []
    if year == datetime.datetime.now().year:
        num_of_months = datetime.datetime.now().month
    for month in range(1, num_of_months + 1):
        monthly_submissions.append(get_monthly_submissions(month, year, subr))
    return pd.concat(monthly_submissions)


# In[12]:

def get_monthly_submissions(number_of_month, year, subr):
    first_day_utc, last_day_utc = get_month_utc_range(number_of_month, year)
    monthly_submissions = get_submissions(first_day_utc, last_day_utc, subr)
    return extract_submission_data(monthly_submissions)


# In[18]:

def extract_submission_data(submissions):
    submission_series = []
    for submission in submissions:
        author = submission.author.name
        sub_id = str(submission.id)
        title = submission.title
        self_text= submission.selftext
        score = submission.score
        created_utc = submission.created_utc
        url = submission.url
        data = [sub_id, author, title, self_text, score, created_utc, url]
        submission_series.append(pd.Series(data, submission_fields))
    return pd.DataFrame(submission_series, columns = submission_fields)


# In[188]:

def extract_comment_data(comments, par_sub_id):
    comment_series = []
    for comment in comments:
        if comment.__class__.__name__ != 'MoreComments':
            author = comment.author
            com_id = str(comment.id)
            body = comment.body
            score = comment.score
            created_utc = comment.created_utc
            ups = comment.ups
            downs = comment.downs
            data = [par_sub_id, com_id, author, body, created_utc, score, ups, downs]
            comment_series.append(pd.Series(data, comment_fields))
    return pd.DataFrame(comment_series, columns = comment_fields)


# In[14]:

def save_dataframe(df, path):
    df.to_csv(path)


# In[15]:

def get_file_name(year, month):
    return datetime.date(year, month, 1).strftime('%B') + '-' + str(year) + '.csv'


# In[16]:

def concat_monthly_dataframes(year):
    monthly_dataframes = []
    num_of_months = 12
    if year == datetime.datetime.now().year:
        num_of_months = datetime.datetime.now().month
    for month in range(1, num_of_months + 1):
        monthly_dataframes.append(pd.read_csv(get_file_name(year, month)))
    yearly_submissions = pd.concat(monthly_dataframes)
    yearly_submissions.reset_index(inplace=True, drop=True)
    return yearly_submissions


#submissions = pd.read_csv('DarkNetSubredditSubmissions.csv')
#get_all_comments(submissions).to_csv('DarkNetComments.csv')

sr_submissions = get_yearly_submissions(2017, silk_road_sub)
save_dataframe(sr_submissions, "Silk_Road_Submissions.csv")



# In[ ]:



