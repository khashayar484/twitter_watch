from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import json
import data_gathering.sentiment as sentiment_aggregator
import data_gathering.tweet as twitter_aggregator
from datetime import datetime
import webpage.processor as dispatcher
from dataclasses import dataclass

app = Flask(__name__,  template_folder = "template" , static_folder="static")
picfolder = os.path.join('static' , 'images')

def check_update(threshold, author):
    """
    set update threshold for 6 hours.
    """
    _file = f"source\\{author}_reply.csv"
    if  os.path.isfile(_file):
        print('......... file is updated .........')
        df = pd.read_csv(_file)
        df = df.sort_values(by = ['date'] , ascending=True) 
        last_date =  pd.to_datetime(df['date'].iloc[-1])
        last_date = last_date.replace(tzinfo=None)
        delta = (datetime.now() - last_date).total_seconds()/3600
        print('--------> delta is ' , delta , ' hours')
        if delta > threshold: 
            print('......... update is needed .........')
            # sentiment_aggregator.update_sentiment("source")
            # twitter_aggregator.update_twitter()
    else:
        print('......... file not exist .........')
        # sentiment_aggregator.update_sentiment("source")
        # twitter_aggregator.update_twitter()
    return _file

class Info:
    def __init__(self , source_adr):
        self.user = None
        self.source_address = None 
        self.source = source_adr
    
info_tabel = Info(source_adr="source")

@app.route("/", methods = ['GET' , 'POST'])
def homepage():
    return render_template("homepage.html")

@app.route('/accounts', methods = ["GET", "POST"])
def get_indices():
    user = request.form['user']
    source_file = check_update(threshold = 12, author = user)  ## update in each 6 hours.
    print(" ::::: update in each 6 hours ::::: ") 
    active_accounts, numbers, high_active_user, high_active_num = dispatcher.accout_data_aggregator(source_file_ = source_file)
    
    info_tabel.user, info_tabel.source_address = user, source_file
    return jsonify({"active_accounts" : active_accounts , 'numbers' :numbers , "high_active_user" : high_active_user, "high_active_num" : high_active_num})

@app.route('/tweets', methods = ["GET", "POST"])
def tweets():
    print("info_tabel.source " , info_tabel.source)

    conversations, date  = dispatcher.account_threads(source_file_ = f"{info_tabel.source}\\{info_tabel.user}_tweet.csv")
    short_conv = conversations[:20]
    short_date = date[:20]

    return jsonify({"conversations" : short_conv, "date" : short_date})

@app.route('/replies', methods = ["GET", "POST"])
def replies():
    conversations, date  = dispatcher.reply_threads(source_file_ = f"{info_tabel.source}\\{info_tabel.user}_reply.csv")
    conversations = conversations[:20]
    date = date[:20]

    return jsonify({"conversations" : conversations, "date" : date})

@app.route('/sentiment/replies', methods = ["GET", "POST"])
def replies_sentiment():
    data = dispatcher.accounts_setiment(source_file_ = f"{info_tabel.source}\\{info_tabel.user}_reply.csv")
    date_range = data.index.tolist()
    sentiments = data.values.tolist()
    names = list(data.columns)

    return jsonify({ "date_range" : date_range , "sentiments" : sentiments , 'names' : names})

@app.route('/sentiment/tweets', methods = ["GET", "POST"])
def tweets_sentiment():
    data = dispatcher.accounts_setiment(source_file_ = f"{info_tabel.source}\\{info_tabel.user}_tweet.csv")
    date_range = data.index.tolist()
    sentiments = data.values.tolist()
    names = list(data.columns)

    return jsonify({ "date_range" : date_range , "sentiments" : sentiments , 'names' : names})

if __name__ == "__main__":
    app.run(debug=False)
    