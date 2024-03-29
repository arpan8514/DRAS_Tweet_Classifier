# -*- coding: utf-8 -*-

import time
import sys
import getopt
import datetime
import codecs
import os

from Tweet import Tweet
from TweetCriteria import TweetCriteria
from TweetManager import TweetManager
#------------------------------------------------------------------------------#

def main(argv):

    if len(argv) == 0:
        print ('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        print ("read help")
        """\nTo use this jar, you can pass the folowing attributes:
    username: Username of a specific twitter account (without @)
       since: The lower bound date (yyyy-mm-aa)
       until: The upper bound date (yyyy-mm-aa)
 querysearch: A query text to be matched
   maxtweets: The maximum number of tweets to retrieve

 \nExamples:
 # Example 1 - Get tweets by username [barackobama]
 python Export.py --username 'barackobama' --maxtweets 1\n

 # Example 2 - Get tweets by query search [europe refugees]
 python Export.py --querysearch 'europe refugees' --maxtweets 1\n

 # Example 3 - Get tweets by username and bound dates [barackobama, '2015-09-10', '2015-09-12']
 python Export.py --username 'barackobama' --since 2015-09-10 --until 2015-09-12 --maxtweets 1\n"""
        return
 
    try:
        opts, args = getopt.getopt(argv, "", ("username=", "since=", "until=", "querysearch=", "maxtweets=", "language="))
        
        tweetCriteria = TweetCriteria()
        
        for opt,arg in opts:
            if opt == '--username':
                tweetCriteria.username = arg
                
            elif opt == '--since':
                tweetCriteria.since = arg
                
            elif opt == '--until':
                tweetCriteria.until = arg
                
            elif opt == '--querysearch':
                tweetCriteria.querySearch = arg
                
            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)
                
            elif opt == '--language':
                tweetCriteria.language = arg
        
        outputFile = codecs.open("output_got.txt", "w+", "utf-8")
        
        #outputFile.write('text')
        
        print ('Searching...\n')
        
        def receiveBuffer(tweets):
            for t in tweets:
                #outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink)))
                t1 = '"' + t.text + '"' 
                #outputFile.write(('\n%s' % (t.text))+ os.linesep)
                outputFile.write(('\n%s' % t1)+ os.linesep)
                

            outputFile.flush();
            print ('More %d saved on file...\n' % len(tweets))
        
        TweetManager.getTweets(tweetCriteria, receiveBuffer)
        
    except arg:
        print ('Arguments parser error, try -h' + arg)
    finally:
        outputFile.close()
        print ('Scraping Complete.')

if __name__ == '__main__':
    main(sys.argv[1:])
