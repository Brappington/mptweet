# import flask class
from flask import Flask, render_template
import os
import sqlite3
import tweepy
import json

# set root directory path comment out this line when testing 
#os.chdir('/home/mptwitter/mptweet/')
# instance of the flask class is our WSGI application
# we use __name__ so that it can adapt to be imported as a module.
app = Flask(__name__)

# instance of sqlite datbase
db = "app/database/mptweet.db"

# read the json  data of Parties for the database
with open('app/static/data/partyData.json', 'r') as myfile:
    data=myfile.read()
# parse file
partydata = json.loads(data)

# read the json  data of MPs for the database
with open('app/static/data/mpDataAll.json', 'r') as myfile:
    data=myfile.read()
# parse file
mpdata = json.loads(data)

# twitter api config
consumer_key = 'NtLIPnCyyeEiiEWl3LWPCNssl'
consumer_secret = 'nkOUbyh5mUeVp3pxO5mjqbBIJFxaQYNoUN0ybcPJPC3fwnEcTI'
access_token = '1090976401333858304-Vu5Y7y7KUyxpblwkzegs7VMxfKbXTt'
access_secret = 'xLZBZxojXvpPMIE4tJnylTJ7DIZLKZauLytyzSUb2Y1s6'
# database module

# delete the database 
def deleteDatabase(cursor):
    # drop tables if exist
    drop_mp = "DROP TABLE IF EXISTS mp"
    drop_party = "DROP TABLE IF EXISTS party"
    drop_status = "DROP TABLE IF EXISTS status"
    cursor.execute(drop_mp)
    cursor.execute(drop_party)
    cursor.execute(drop_status)

def createTables(cursor):
    # create party table
    create_party = "CREATE TABLE party (name VARCHAR(255) PRIMARY KEY NOT NULL, colour CHECK(colour IN ('red', 'blue', 'yellow', 'green', 'orange', 'black', 'lime', 'silver', 'olive')) NOT NULL)"
    # create mp table
    create_mp = "CREATE TABLE mp (user_id VARCHAR(255) PRIMARY KEY NOT NULL, name VARCHAR(255) NOT NULL, gender CHECK(gender IN ('Male', 'Female')) NOT NULL, party VARCHAR(255) NOT NULL, FOREIGN KEY (party) REFERENCES party(name))"
    # create status update
    create_status = "CREATE TABLE status (id_str VARCHAR(255) PRIMARY KEY, created_at TEXT, user_id VARCHAR(255) NOT NULL, favorite_count MEDIUMINT, retweet_count MEDIUMINT, FOREIGN KEY (user_id) REFERENCES mp(user_id))"
    cursor.execute(create_party)
    cursor.execute(create_mp)
    cursor.execute(create_status)

# add data from mpdata and party data json files stored in app/static/data/
def addJsonData():
    # add data from json
    for y in mpdata["mps"]:
        addMP(y["user_id"], y["name"], y["gender"], y["party"])
    for x in partydata["parties"]:
        addParty(x["name"], x["colour"])


# initialise a new database with provided data.
def intialiseDB():
    # create database and tables
        # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # delete previous database and create new
    deleteDatabase(c)
    createTables(c)
    # commit database changes
    conn.commit()
    # close connection
    conn.close()
    # add data from json
    addJsonData()
    # get user_ids for MPs in database
    mps = getUserIds()
    # get tweets from mps and add to database
    allMPTweets(mps) 

# updates the database without deleting it
def updateDB():
    # get user_ids for MPs in database
    mps = getUserIds()
    # get tweets from mps and add to database
    allMPTweets(mps)

# mp module

# add mp to database
def addMP(user_id, name, gender, party):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' INSERT INTO mp(user_id, name, gender, party)
    VALUES(?,?,?,?)'''
    try:
        c.execute(sql, (user_id, name, gender, party))
        print(user_id, name, gender, party)
    except sqlite3.IntegrityError:
        print("MP ",  name, " already exists!")
    # commit database changes
    conn.commit()
    # close connection
    conn.close()

# add status to database


def addStatus(id_str, created_at, user_id, favorite_count, retweet_count):
    # connect to it
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' INSERT INTO status(id_str, created_at, user_id, favorite_count, retweet_count)
    VALUES(?,?,?,?,?)'''
    try:
        c.execute(sql, (id_str, created_at, user_id,
                        favorite_count, retweet_count))
        print('adding tweet: ')
        print(id_str, created_at, user_id, favorite_count, retweet_count)
    except sqlite3.IntegrityError:
        print('Tweet already exists!')
    # commit database changes
    conn.commit()
    # close connection
    conn.close()


# add party to the database

def addParty(name, colour):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' INSERT INTO party(name, colour) VALUES(?,?)'''
    try:
        c.execute(sql, (name, colour))
        print(name, colour)
    except sqlite3.IntegrityError:
        print(name, ' already exists!')
    # commit database changes
    conn.commit()
    # close connection`
    conn.close()

# returns name of mp from database as string


def getMPName(user_id):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT name FROM mp WHERE user_id =?'''
    c.execute(sql, (user_id,))
    fetch = c.fetchone()
    # get string of name only
    name = fetch[0]
    print(name)
    # close connection
    conn.close()
    return name

# returns name of MPs party

def getMPColour(user_id):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT colour from party INNER JOIN mp ON party.name = mp.party WHERE mp.user_id = ?'''
    c.execute(sql, (user_id,))
    fetch = c.fetchone()
    # get string of name only
    colour = fetch[0]
    print(colour)
    # close connection
    conn.close()
    return colour
# return user_ids for all mps in database as a list


def getUserIds():
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT user_id FROM mp'''
    ids = [id[0] for id in c.execute(sql)]
    print(ids)
    # close connection
    conn.close()
    return ids

# gets recent tweets for mp with provided user_id and adds them to database


def getAllTweets(user_id):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialise tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # initialize a list to save all the  Tweets
    alltweets = []

    # make first request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(user_id=user_id, count=200, include_rts=False)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save id of the oldest tweet minus one
    oldest = alltweets[-1].id - 1

    # keep getting tweets until there are no tweets left to get
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        # all subsequent requests use the max_id param to prevent duplicates
        # added include_rts=False to not include retweets
        new_tweets = api.user_timeline(
            user_id=user_id, count=200, max_id=oldest, include_rts=False)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet minus one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))
    # iterates through tweets and adds each tweet to database using addStatus()
    for tweet in alltweets:
        addStatus(tweet.id_str, tweet.created_at,
                  tweet.user.id_str, tweet.favorite_count, tweet.retweet_count)

# gets recent tweets for mps from list and adds them to database


def allMPTweets(mp_ids):
    for user_id in mp_ids:
        getAllTweets(user_id)
        print(getMPName(user_id), ' MP tweets imported to database')

# These functions return the average engagement for mps, genders and parties respectively


def getMPEngagement(user_id):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # get total retweet_count and favorite_count for user_id
    favesql = ''' SELECT SUM(favorite_count) FROM status WHERE user_id = ?'''
    c.execute(favesql, (user_id,))
    fetch = c.fetchone()
    totalfavorite = fetch[0]
    print("Total favorite: ", totalfavorite)
    # find sum of total retweet_count and favorite_count
    retweetsql = ''' SELECT SUM(retweet_count) FROM status WHERE user_id = ?'''
    c.execute(retweetsql, (user_id,))
    fetch = c.fetchone()
    totalretweet = fetch[0]
    print("Total retweet: ", totalretweet)
    # get total number of status items for user_id
    totalsql = ''' SELECT COUNT(*) FROM status WHERE user_id = ?'''
    c.execute(totalsql, (user_id,))
    fetch = c.fetchone()
    total = fetch[0]
    print("Total tweets: ", total)
    # find average
    avg = round((totalretweet + totalfavorite) / total)
    print("Average engagement: ", avg)
    # close connection
    conn.close()
    # return average
    return avg


def getGenderEngagement(gender):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # get total retweet_count and favorite_count for user_id
    favesql = ''' SELECT sum(favorite_count) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ?'''
    c.execute(favesql, (gender,))
    fetch = c.fetchone()
    totalfavorite = fetch[0]
    print("Total favorite: ", totalfavorite)
    # find sum of total retweet_count and favorite_count
    retweetsql = ''' SELECT sum(retweet_count) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ?'''
    c.execute(retweetsql, (gender,))
    fetch = c.fetchone()
    totalretweet = fetch[0]
    print("Total retweet: ", totalretweet)
    # get total number of status items for user_id
    totalsql = ''' SELECT COUNT(*) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ?'''
    c.execute(totalsql, (gender,))
    fetch = c.fetchone()
    total = fetch[0]
    print("Total tweets: ", total)
    # find average
    avg = round((totalretweet + totalfavorite) / total)
    print("Average engagement: ", avg)
    # close connection
    conn.close()
    # return average
    return avg


def getPartyEngagement(party):
     # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # get total retweet_count and favorite_count for user_id
    favesql = ''' SELECT sum(favorite_count) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ?'''
    c.execute(favesql, (party,))
    fetch = c.fetchone()
    totalfavorite = fetch[0]
    print("Total favorite: ", totalfavorite)
    # find sum of total retweet_count and favorite_count
    retweetsql = ''' SELECT sum(retweet_count) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ?'''
    c.execute(retweetsql, (party,))
    fetch = c.fetchone()
    totalretweet = fetch[0]
    print("Total retweet: ", totalretweet)
    # get total number of status items for user_id
    totalsql = ''' SELECT COUNT(*) FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ?'''
    c.execute(totalsql, (party,))
    fetch = c.fetchone()
    total = fetch[0]
    print("Total tweets: ", total)
    # find average
    avg = round((totalretweet + totalfavorite) / total)
    print("Average engagement: ", avg)
    # close connection
    conn.close()
    # return average
    return avg


# returns list of mp name and average engagement


def getMPs():
    mps = getUserIds()
    mplist = []
    for user_id in mps:
        mplist.append([getMPName(user_id), getMPEngagement(user_id), getMPColour(user_id)])
    mplist = sorted(mplist, key=lambda x: x[1], reverse=True)
    print(mplist[:9])
    return mplist[:9]

# returns list of gender and average engagement


def getGenders():
    genders = ['Male', 'Female']
    list = []
    for gender in genders:
        list.append([gender, getGenderEngagement(gender)])
    print(list)
    return list

# return list of party and average engagement


def getParties():
    parties = getPartyNames()
    list = []
    for party in parties:
        list.append([party, getPartyEngagement(
            party), 'color: ' + getColour(party)])
    print(list)
    return list


# returns list of names for parties in the database


def getPartyNames():
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT DISTINCT name FROM party '''
    names = [id[0] for id in c.execute(sql)]
    print(names)
    # close connection
    conn.close()
    return names


# returns the colour of a party in the database


def getColour(name):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT colour FROM party WHERE name = ? '''
    c.execute(sql, (name,))
    fetch = c.fetchone()
    colour = fetch[0]
    print("The colour of", name, "is:", colour)
    return colour

# get most engaged tweets
# mp

def mostEngagedMPTweet(mp):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT id_str FROM (SELECT  MAX(favorite_count + retweet_count), id_str FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE
    name = ? AND
    created_at > date('now','-1 month')) '''
    c.execute(sql, (mp,))
    fetch = c.fetchone()
    tweetid = fetch[0]
    print("The id of the tweet is: ", tweetid)
    return(getEmbed(tweetid))

# gender

def mostEngagedGenderTweet(gender):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT id_str FROM (SELECT MAX(favorite_count + retweet_count), id_str FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ? AND
    created_at > date('now','-1 month'))'''
    c.execute(sql, (gender,))
    fetch = c.fetchone()
    tweetid = fetch[0]
    print("The id of gender most engaged tweet is: ", tweetid)
    return(getEmbed(tweetid))

# party

def mostEngagedPartyTweet(party):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT id_str FROM (SELECT MAX(favorite_count + retweet_count), id_str FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ? AND
    created_at > date('now','-1 month'))'''
    c.execute(sql, (party,))
    fetch = c.fetchone()
    tweetid = fetch[0]
    print("The id of the party most engaged tweet is: ", tweetid)
    return(getEmbed(tweetid))
    

# get embededed tweet
def getEmbed(tweetid):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    embed_tweet = api.get_oembed(tweetid)
    print(embed_tweet)
    return(embed_tweet["html"])

# find the maximum value for the 2nd item in list of lists

def myMax(listoflists):
    if not listoflists:
        raise ValueError('empty list')
    maximum = listoflists[0]
    for item in listoflists:
        # Compare values by their second element.
        if item[1] > maximum[1]:
            maximum = item
    return maximum


# flask

# route() decorator tells Flask what URL should trigger our function
@app.route('/')
def main():
    mplist = getMPs()
    mptweet = mostEngagedMPTweet(myMax(mplist)[0])
    genderlist = getGenders()
    gendertweet = mostEngagedGenderTweet(myMax(genderlist)[0])
    partylist = getParties()
    partytweet = mostEngagedPartyTweet(myMax(partylist)[0])
    return render_template('index.html', mplist=mplist, mptweet=mptweet,genderlist=genderlist, gendertweet=gendertweet, partylist=partylist, partytweet=partytweet)

@app.route('/test')
def test():
    intialiseDB()
    return 'database updated'

if __name__ == "__main__":
    app.run(debug=True)
