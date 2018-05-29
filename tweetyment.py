# -*- coding: utf-8 -*-
"""
Created on Thu May 17 11:29:34 2018

@author: Amjee
"""

import tweepy
import re
from tweepy import Stream
from tweepy.streaming import StreamListener
from textblob import TextBlob
from credentials import cred
import json
import time
import sqlite3

conn = sqlite3.connect('tweeter.db')
c = conn.cursor()
    
access_key= cred['access_key']
access_token= cred['access_token']
customer_key=cred['customer_key']
customer_token= cred['customer_token']

class Listener(StreamListener):
    
    def on_connect(self):
        print("Connection established")
    
    def on_disconnect(self):
        print("Disconnected")
        
    def on_data(self,status):  
        
        try:
            datajson = json.loads(status)
            data_tweet = datajson["text"].encode('utf-8')
            date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(datajson['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            #time_ms = date_time.encode('ISO-8859-1').strip()
            #pattern_re = ['(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?','(RT)(^|[^@\w])@(\w{1,15})\b.']
            pat1 = r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'
            pat2 = r'(RT)(^|[^@\w])@(\w{1,15})\b.'
            line = data_tweet.decode('utf-8')
            clean1 = re.sub(pat2,'',line)           #removes the RT
            clean2 = re.sub(pat1,"",clean1)         #removes the urls 
            clean3 = clean2.replace('\n', ' ')      # removes the linebreaks

            analyse = TextBlob(clean2)
            sentiment_value = analyse.sentiment.polarity
            #graph_output = {'sv':str(sentiment_value),'dt':str(date_time)}
            #tweetid = datajson["id"]
            c.execute("INSERT INTO sentiment (datetime,sentiment, tweet) VALUES (?, ?, ?)",
                  (date_time, sentiment_value, clean3))
            conn.commit()
            
            #with open('tweetytext.csv','a') as tf:
            #     tf.write(str(date_time.encode('ISO-8859-1').strip())+","+str(sentiment_value)+","+str(clean3)+"\n")
            #print(data_tweet.decode('utf-8'), flush = True)
        except(UnicodeEncodeError,KeyError,tweepy.TweepError,ConnectionError):
            print("!!!")
            
    
    def on_status(self, status):
        id_str = status.id_str
        print( id_str )
        
        
    def on_error( self, status ):
        if status == 420:
            return False
        else:
            print(status)
                
           
def authenticate():
    auth = tweepy.OAuthHandler(access_key,access_token)
    setauth = auth.set_access_token(customer_key,customer_token)
    api = tweepy.API(auth)
    #tweets = api.search(search_string)
      
    '''for tweet in tweets:
        print(tweet.text)
        analyse = TextBlob(tweet.text)
        print(analyse.sentiment)'''
        
    return api


def create_table():
    
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(datetime REAL, sentiment REAL, tweet TEXT)")
        c.execute("CREATE INDEX fast_datetime ON sentiment(datetime)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        conn.commit()
    except Exception as e:
        print(str(e))
create_table()

while True:

    try:
        returned_api = authenticate()
        stream = Stream(returned_api.auth,Listener())
        stream.filter(languages=['en'],track=["a","e","i","o","u"])
        
    except Exception as e:
        print(str(e))
        time.sleep(5)