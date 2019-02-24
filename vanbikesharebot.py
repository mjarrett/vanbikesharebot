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
tddf = mobi.load_csv(workingdir+'taken_daily_df.csv')
sdf = mobi.get_stationsdf(workingdir)

total_trips = int(tddf.loc[d].sum())



# Get nth rank in current year
y = yesterday.strftime('%Y')
rankdf = tddf[y].sum(1).sort_values(ascending=False).reset_index()
rank = rankdf[rankdf['time']==yesterday].index[0] + 1


# Check that we still have data to the beginning of the year. If not tweet for help
jan01 = y + '-01-01'
trips_jan01 = int(tddf.loc[jan01].sum())
if trips_jan01 < 1:
    api.update_status("@mikejarrett_ Help! I'm not working properly today")
    raise ValueError("We need data going back to January 1st for this to work")

    
    # This is magic from Stack Overflow
def ordinal(n):
    if n == 1:
        return ""
    return " {}{}".format(n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

rankstring = ordinal(rank)


# Decide whether a ranking gets an exclamation mark
if rank < 20:
    punct = '!'
else:
    punct = '.'


# Get other stats
status = mobi.get_status(workingdir)

active_stations = sdf.loc[sdf['active'],'name']

a24df = ahdf.loc[d,active_stations].sum()
station24h = a24df.idxmax()
station24hmin = a24df.idxmin()

maxstationtrips = int(a24df.max())
minstationtrips = int(a24df.min())


nstationsmax = len(a24df[a24df == maxstationtrips])
nstationsmin = len(a24df[a24df == minstationtrips])



if nstationsmax > 1:
    max_others_string = "and {} others".format(nstationsmax-1)
else: 
    max_others_string = ""
if nstationsmin > 1:
    min_others_string = "and {} others".format(nstationsmin-1)
else:
    min_others_string = ""

test = False
if len(sys.argv)>2 and sys.argv[2] == '--test':
    test = True

if sys.argv[1] == '--summary':


    # Text string
    s ="""Yesterday there were approximately {} mobi trips. That's the{} most this year{}
Active stations: {}
Active bikes: {}
Most used station: {} {} ({} trips)
Least used station: {} {} ({} trips)
#bikeyvr""".format(total_trips,rankstring,punct,
                   status['stations'],status['bikes'],
                   station24h,max_others_string,maxstationtrips,
                   station24hmin,min_others_string,minstationtrips)



    # Upload images
    ims = ['/var/www/html/mobi/images/lastweek_hourly_yesterday.png',
           '/var/www/html/mobi/images/yesterday_cumsum.png',
           '/var/www/html/mobi/images/lastmonth_daily_yesterday.png',
           '/var/www/html/mobi/images/station_map_yesterday.png'
           ]
    media_ids = [api.media_upload(x).media_id for x in ims]

    
    if test:
        print(s)
        print('-----------')
        print(ims)
        print('{}/280 chars'.format(len(s)))        
    else:
        api.update_status(s, media_ids=media_ids)


elif sys.argv[1] == '--ani':
    s = """Watch yesterday's hourly @mobi_bikes station activity #bikeyvr"""
    ims = ['/var/www/html/mobi/images/station_ani_yesterday.gif']
    media_ids = [api.media_upload(x).media_id for x in ims]    
    if test:
        print(s)
        print('-----------')
        print(ims)
        print('{}/280 chars'.format(len(s)))        
    else:
        api.update_status(s, media_ids=media_ids)
 


    
