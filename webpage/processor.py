import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math 

def accout_data_aggregator(source_file_):
    active_account = pd.read_csv(source_file_ , index_col=0)
    active_account_activity = active_account['user'].value_counts()
    
    user_name = active_account_activity.index.tolist()
    activity_num = active_account_activity.values.tolist()
    
    valu_value_ = pd.Series(active_account_activity.values).value_counts()
    high_active_user, high_active_num = user_name[:20] , activity_num[:20]
    
    how_many_people = valu_value_.values.tolist()
    how_many_times = valu_value_.index.tolist()

    return how_many_people, how_many_times, high_active_user, high_active_num

def account_threads(source_file_):
    active_account = pd.read_csv(source_file_ , index_col=0)
    
    conversations, date = active_account['conversation'].values.tolist(), active_account['date'].values.tolist()
    
    return conversations, date 

def reply_threads(source_file_):
    active_account = pd.read_csv(source_file_ , index_col=0)
    conversations, date = active_account['conversation'].values.tolist(), active_account['date'].values.tolist()
    
    return conversations, date 

def daily_polarity_calculator( dataframe, date_col, weight_col, value_col):
  train_set = dataframe.copy(deep = True)
  train_set['datetime'] = pd.to_datetime(train_set[date_col])
  train_set = train_set.sort_values(by = ["datetime"])
  daily_simple_polarity = train_set.groupby(train_set.datetime.dt.date)[value_col].mean()

  # train_set['day'] = train_set['datetime'].apply(lambda x : x.strftime('%Y-%m-%d'))
  g = train_set.groupby(train_set.datetime.dt.date)
  train_set['wa'] = train_set[f'{weight_col}'] / g[f'{weight_col}'].transform("sum") * train_set[value_col]
  daily_weighted_polarity = g.wa.sum()

  dd = pd.concat([daily_simple_polarity , daily_weighted_polarity] , axis = 1)
  dd.columns = [f'simple_{value_col}' , f'weighted_{value_col}']

  return dd

def accounts_setiment(source_file_):
  active_account = pd.read_csv(source_file_ , index_col=0) 
  sentiments = [-1 ,0 , 1] 
  active_account['bert_compound'] = active_account['bert_sentiment'].apply(lambda x : np.sqrt(sum([j**2 for j in eval(x).values()])) )
  active_account['bert_direction'] = active_account['bert_sentiment'].apply(lambda x : max([k for k in eval(x).values()]) * sentiments[np.argmax([k for k in eval(x).values()])] )
  active_account['bert_sentiment'] = active_account['bert_compound'] * active_account['bert_direction']
  
  active_account['polarity_value'] = active_account['polarity'].apply(lambda x : eval(x)[1])
  active_account['polarity_direction'] =  active_account['polarity'].apply(lambda x : 1 if eval(x)[0] == 'Positive' else -1 if eval(x)[0] == 'Negative' else 0)
  active_account['polarity_sentiment'] = active_account['polarity_direction'] * active_account['polarity_value']
  
  active_account['vader_sentiments'] = active_account['vader_sentiment'].apply(lambda x : list(eval(x).values())[3])
  active_account['weights'] = (active_account['replies number'] + active_account['likes number'] + active_account['rewteets number']) / 3
  

  daily_bert = daily_polarity_calculator(dataframe = active_account , date_col='date' , weight_col='weights' , value_col= 'bert_sentiment')
  daily_polarity = daily_polarity_calculator(dataframe = active_account , date_col='date' , weight_col='weights' , value_col= 'polarity_sentiment')
  daily_vader = daily_polarity_calculator(dataframe = active_account , date_col='date' , weight_col='weights' , value_col= 'vader_sentiments')
  
  daily_sentiment_info = pd.concat([daily_bert, daily_polarity, daily_vader] , axis = 1)

  return daily_sentiment_info


# accounts_setiment("source\\ylecun_tweet.csv")