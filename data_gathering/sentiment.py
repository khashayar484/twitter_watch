
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from textblob import TextBlob
from wordcloud import WordCloud
from tqdm import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer
import re
from scipy.special import softmax
import os
import pandas as pd

stopwordlist = ['a', 'about', 'above', 'after', 'again', 'ain', 'all', 'am', 'an',
             'and','any','are', 'as', 'at', 'be', 'because', 'been', 'before',
             'being', 'below', 'between','both', 'by', 'can', 'd', 'did', 'do',
             'does', 'doing', 'down', 'during', 'each','few', 'for', 'from',
             'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here',
             'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in',
             'into','is', 'it', 'its', 'itself', 'just', 'll', 'm', 'ma',
             'me', 'more', 'most','my', 'myself', 'now', 'o', 'of', 'on', 'once',
             'only', 'or', 'other', 'our', 'ours','ourselves', 'out', 'own', 're','s', 'same', 'she', "shes", 'should', "shouldve",'so', 'some', 'such',
             't', 'than', 'that', "thatll", 'the', 'their', 'theirs', 'them',
             'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
             'through', 'to', 'too','under', 'until', 'up', 've', 'very', 'was',
             'we', 'were', 'what', 'when', 'where','which','while', 'who', 'whom',
             'why', 'will', 'with', 'won', 'y', 'you', "youd","youll", "youre",
             "youve", 'your', 'yours', 'yourself', 'yourselves']

import string
english_punctuations = string.punctuation
punctuations_list = english_punctuations


class SentimetAnalyzor:
  model_name = "cardiffnlp/twitter-roberta-base-sentiment"

  def __init__(self):
    self.bert_model = AutoModelForSequenceClassification.from_pretrained(SentimetAnalyzor.model_name)
    self.bert_tokenizer = AutoTokenizer.from_pretrained(SentimetAnalyzor.model_name)
    self.bert_config = AutoConfig.from_pretrained(SentimetAnalyzor.model_name)

  @staticmethod
  def getPolarityScore(text):
    return TextBlob(text).sentiment.polarity  
  
  @staticmethod
  def getSentiment(polarity_score):
    if polarity_score < 0:  
      return 'Negative'
    elif polarity_score == 0:
      return 'Neutral'
    else:
      return 'Positive'

  def text_polarity(self, post):
    """

    """
    polarity = SentimetAnalyzor.getPolarityScore(post)
    sentiment = SentimetAnalyzor.getSentiment(polarity)

    return sentiment, polarity
  
  def hugging_face(self, post):
    """ 
    Labels: 0 -> Negative; 1 -> Neutral; 2 -> Positive

    """   

    ## @account_name to specific token @user
    roberta_input = " ".join(['@user' if word.startswith('@') and len(word) > 1 else word for word in str(post).split(" ")])
    ## replce http
    roberta_input = " ".join(['http' if word.startswith('http') else word for word in str(post).split(" ")])
    # config = AutoConfig.from_pretrained(model_name)

    encoded_input = self.bert_tokenizer(post, return_tensors='pt')

    output = self.bert_model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    labels = ['Negative', 'Neutral' , 'Positive']
    res = {labels[i]: scores[i] for i in range(len(scores))}

    return res

  def vader(self, post):
    sia = SentimentIntensityAnalyzer()
    vader_polarity = sia.polarity_scores(post)
    return vader_polarity

  def clean_data(self, data):
    ## Cleaning and removing the above stop words list from the tweet text
    cleaned_data = " ".join([word.lower() for word in str(data).split() if word not in stopwordlist])
    ## remove puchuation
    cleaned_data = str(cleaned_data).translate(str.maketrans('', '', string.punctuation))
    ## Cleaning and removing repeating characters
    cleaned_data = re.sub(r'(.)1+', r'1', cleaned_data)
    ## Cleaning and removing URLs
    cleaned_data = re.sub('((www.[^s]+)|(https?://[^s]+))',' ',cleaned_data)
    ## Cleaning and removing numeric numbers
    cleaned_data =  re.sub('[0-9]+', '', cleaned_data)
    ## Getting tokenization of tweet text
    token = cleaned_data
    cleaned_data =  "".join(word for word in token)

    return cleaned_data, token


def update_sentiment(file_source):
  sentiment_analyzor = SentimetAnalyzor()

  for file in os.listdir(f'{file_source}//.'):
    print('---------> file is ' , file)
    
    if "csv" in file:
      
      df = pd.read_csv(f"{file_source}//{file}" , index_col = 0)
      not_need_updated, need_updated = df.loc[df['cleaned_data'].notna()], df.loc[df['cleaned_data'].isna()]
      if len(need_updated) > 0 : 
        for index, tweet in enumerate(need_updated['conversation']):
          print('--------> update record is ' , index , ' remaining ' , len(need_updated) - index)
          try:
            clean_data,tokenized_data = sentiment_analyzor.clean_data(tweet)
            polarity = sentiment_analyzor.text_polarity(clean_data)
            bert_score = sentiment_analyzor.hugging_face(tweet)
            vader_score = sentiment_analyzor.vader(clean_data)
            record = pd.DataFrame({"date" : [need_updated['date'].iloc[index]],
                                    "user" : [need_updated['user'].iloc[index]],
                                    "conversation" : [tweet],
                                    "replies number" : [need_updated['replies number'].iloc[index]],
                                    "likes number" : [need_updated['likes number'].iloc[index]],
                                    "rewteets number" : [need_updated['rewteets number'].iloc[index]],
                                    "cleaned_data" : [clean_data],
                                    'token_data' : [tokenized_data],
                                    'polarity' : [polarity] ,
                                    'bert_sentiment' : [bert_score],
                                    "vader_sentiment" : [vader_score]})
        
            not_need_updated = not_need_updated.append(record)
            tot = pd.concat([not_need_updated , need_updated.iloc[index: , :]], axis = 0)
            p1 = tot.duplicated(['date', 'user'], keep=False)
            p2 = tot['cleaned_data'].isna()
            p = p1 & p2
            tot = tot[~p]

            tot.to_csv(f"{file_source}//{file}", mode='w', header = True) 

          except:
            print('-------------> something went wrong')
            break
      else:
        print('-------------> everything was up ot dated')

