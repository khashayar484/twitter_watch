from datetime import datetime, timedelta
import os
import pandas as pd
import snscrape.modules.twitter as sntwitter

class TwitterAggregator:
  
  until = datetime.now().strftime('%Y-%m-%d')
  since = "2023-02-1"
  
  def __init__(self, data , author, mode):
    self.repository = data
    self.author = author
    self.mode = mode
    self.first_date = None
    self.last_date = None
    self.dir = 'source'
    self.file_path = f"source//{self.author}_{self.mode}.csv"

  def _file_existance_check(self):
    if not os.path.isfile(self.file_path):
      if not os.path.exists(self.dir): os.makedirs(self.dir)
      df = pd.DataFrame(columns = self.repository.columns)
      df.to_csv(self.file_path)
      return TwitterAggregator.since, TwitterAggregator.until
    
    else:
      self.repository = pd.read_csv(self.file_path, index_col = 0)
      if len(self.repository) > 1 : 
        self.repository = self.repository.drop_duplicates()
        self.repository = self.repository.sort_values(by = ['date'] , ascending=True) 
        _date, self.last_date = pd.to_datetime(self.repository['date'].iloc[0]).strftime('%Y-%m-%d') , pd.to_datetime(self.repository['date'].iloc[-1])

      else:
        _date = TwitterAggregator.until
        
      return TwitterAggregator.since, _date

  def fetch_data(self):
    _start_time, _end_time = self._file_existance_check()
    if _start_time != _end_time: ## update threshold
      _twitter_mode = f'from:@{self.author} since:{_start_time} until:{_end_time}' if self.mode == 'tweet' else f'to:{self.author}  since:{_start_time} until:{_end_time} ' if self.mode == 'reply' else None
      for index,tweet in enumerate(sntwitter.TwitterSearchScraper(_twitter_mode).get_items()):
        self.repository = self.repository.append({
          "date" : tweet.date,
          "user" : tweet.user.username, 
          "conversation" : tweet.rawContent, 
          "replies number" : tweet.replyCount,
          "likes number" : tweet.likeCount,
          "rewteets number" : tweet.retweetCount
        }, ignore_index = True)
        self.repository.to_csv(self.file_path, mode='w', header = True)

  

def update_twitter():
  print('---------------> update twitter repo ')
  data =  pd.DataFrame(columns = [ 'date' , 'user' , 'conversation' , 'replies number' ,
                                  'likes number' , 'rewteets number', 'cleaned_data', 'token_data' , 'polarity' , 
                                  'bert_sentiment' , 'vader_sentiment']) 
  
  for mode in ['tweet' , 'reply']:
    twitter_aggregator = TwitterAggregator(data , "ylecun" , mode)
    twitter_aggregator.fetch_data()