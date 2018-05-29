# Import our Twitter credentials from credentials.py
from credentials import *
import tweepy
from datetime import date, timedelta
import pandas as pd

import sys
sys.path.append("/home/msj/mobi/")
import mobi
# Mobi data directory
workingdir = '/data/mobi/data/'

# Access and authorize our Twitter credentials from credentials.py
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)



# Get stats for text
yesterday = date.today() - timedelta(1)
d = yesterday.strftime('%Y-%m-%d')

thdf = mobi.load_csv(workingdir+'taken_hourly_df.csv')
ahdf = mobi.load_csv(workingdir+'activity_hourly_df.csv')
sddf = mobi.load_csv(workingdir+'stations_daily_df.csv')

total_trips = int(thdf[d].sum(1).sum())

status = mobi.get_status(workingdir)



active_stations = sddf.loc[d,(sddf.loc[d] >= 0).values].index
a24df = ahdf.loc[d,active_stations].sum()
a24df = a24df[a24df>0]
station24h = a24df.idxmax()
station24hmin = a24df.idxmin()

# Text string
s ="""Yesterday there were approximately {} mobi trips
Active stations: {}
Active bikes: {}
Most used station: {}
Least used station: {}
#bikeyvr""".format(total_trips,status['stations'],status['bikes'],station24h,station24hmin)



# Upload images
ims = ['/var/www/html/mobi/images/lastweek_hourly_yesterday.png',
       '/var/www/html/mobi/images/lastmonth_daily_yesterday.png']
media_ids = [api.media_upload(x).media_id for x in ims]



if len(sys.argv)>1 and sys.argv[1] == '--test':
    print(s)
else:
    # Update status
    api.update_status(s, media_ids=media_ids)
