# import flask class
from flask import Flask, render_template
import sqlite3
import tweepy
# instance of the flask class is our WSGI application
# we use __name__ so that it can adapt to be imported as a module.
app = Flask(__name__)

# instance of sqlite datbase
db = "app/database/mptweet.db"
# twitter api config
consumer_key = 'NtLIPnCyyeEiiEWl3LWPCNssl'
consumer_secret = 'nkOUbyh5mUeVp3pxO5mjqbBIJFxaQYNoUN0ybcPJPC3fwnEcTI'
access_token = '1090976401333858304-Vu5Y7y7KUyxpblwkzegs7VMxfKbXTt'
access_secret = 'xLZBZxojXvpPMIE4tJnylTJ7DIZLKZauLytyzSUb2Y1s6'

# database module


def createtables():
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # drop tables if exist
    drop_mp = "DROP TABLE IF EXISTS mp"
    drop_party = "DROP TABLE IF EXISTS party"
    drop_status = "DROP TABLE IF EXISTS status"
    # create party table
    create_party = "CREATE TABLE party (name VARCHAR(255) PRIMARY KEY NOT NULL, colour CHECK(colour IN ('red', 'blue', 'yellow', 'green', 'orange', 'black')) NOT NULL)"
    # create mp table
    create_mp = "CREATE TABLE mp (user_id VARCHAR(255) PRIMARY KEY NOT NULL, name VARCHAR(255) NOT NULL, gender CHECK(gender IN ('Male', 'Female')) NOT NULL, party VARCHAR(255) NOT NULL, FOREIGN KEY (party) REFERENCES party(name))"
    # create status update
    create_status = "CREATE TABLE status (id_str VARCHAR(255) PRIMARY KEY, created_at TEXT, user_id VARCHAR(255) NOT NULL, favorite_count MEDIUMINT, retweet_count MEDIUMINT, FOREIGN KEY (user_id) REFERENCES mp(user_id))"
    # execute creating tables
    c.execute(drop_mp)
    c.execute(drop_party)
    c.execute(drop_status)
    c.execute(create_party)
    c.execute(create_mp)
    c.execute(create_status)
    # commit database changes
    conn.commit()
    # close connection
    conn.close()

# initialise a new database with provided data.


def intialiseDB():
    # create database and tables
    createtables()
    # add initial data into party table
    addParty('Liberal Democrat', 'yellow')
    addParty('Labour', 'red')
    addParty('Conservative', 'blue')
    addParty('Green', 'green')
    addParty('Scottish Nationalist', 'orange')
    addParty('Independent', 'black')
    # add initial data into mp table
    addMP('14933304', 'Jo Swinson', 'Female', 'Liberal Democrat')
    addMP('80802900', 'Caroline Lucas', 'Female', 'Green')
    addMP('173089105', 'Roberta Blackman-Woods', 'Female', 'Labour')
    addMP('61781260', 'Ed Miliband', 'Male', 'Labour')
    addMP('120236641', 'Mhairi Black', 'Female', 'Scottish Nationalist')
    addMP('19058678', 'Michael Fabricant', 'Male', 'Conservative')
    addMP('14104027', 'Grant Shapps', 'Male', 'Conservative')
    # get user_ids for MPs in database
    mps = get_user_ids()
    # get tweets from mps and add to database
    all_mp_tweets(mps)

# mp module

# add mp to database


def addMP(user_id, name, gender, party):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' INSERT INTO mp(user_id, name, gender, party)
    VALUES(?,?,?,?)'''
    c.execute(sql, (user_id, name, gender, party))
    print(user_id)
    print(name)
    print(gender)
    print(party)
    # commit database changes
    conn.commit()
    # close connection
    conn.close()

# returns name of mp from database as string


def getMPname(user_id):
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

# returns gender of mp from database


def getMPgender(user_id):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT gender FROM mp WHERE user_id =?'''
    c.execute(sql, (user_id,))
    fetch = c.fetchone()
    # get string of name only
    gender = fetch[0]
    print(gender)
    # close connection
    conn.close()
    return gender

# return party of mp from database


def getMPparty(user_id):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT party FROM mp WHERE user_id = ?'''
    c.execute(sql, (user_id,))
    fetch = c.fetchone()
    # get string of name only
    party = fetch[0]
    print(party)
    # close connection
    conn.close()
    return party

# return user_ids for all mps in database as a list


def get_user_ids():
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


def get_all_tweets(user_id):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(user_id=user_id, count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        # all subsequent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(
            user_id=user_id, count=200, max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))
    # iterates through tweets and adds each tweet to database
    for tweet in alltweets:
        addStatus(tweet.id_str, tweet.created_at,
                  tweet.user.id_str, tweet.favorite_count, tweet.retweet_count)

# gets recent tweets for mps from list and adds them to database


def all_mp_tweets(mp_ids):
    for user_id in mp_ids:
        get_all_tweets(user_id)
        print(getMPname(user_id), ' MP tweets imported to database')

# returns the average engagement for a mp


def getAvgEngagement(user_id):
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

# returns list of name, gender, party and average
# engagement for each mp in list


def getAllAvgEngagement():
    mps = get_user_ids()
    list = []
    for user_id in mps:
        list.append([getMPname(user_id), getMPgender(user_id),
                     getMPparty(user_id), getAvgEngagement(user_id)])

    print(list)
    return list

# party module

# add party to the database


def addParty(name, colour):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' INSERT INTO party(name, colour) VALUES(?,?)'''
    c.execute(sql, (name, colour))
    print(name)
    print(colour)
    # commit database changes
    conn.commit()
    # close connection
    conn.close()

# delete party and associated mps from the databass


def deleteParty(name):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' DELETE FROM party WHERE name = ? '''
    c.execute(sql, (name,))
    print('deleting: ', name)
    sql1 = ''' DELETE FROM mp WHERE party = ? '''
    c.execute(sql1, (name,))
    print('deleting associated mps')
    # commit database changes
    conn.commit()
    # close connection
    conn.close()

# returns list of names for parties in the database


def getNames():
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT name FROM party '''
    names = [id[0] for id in c.execute(sql)]
    print(names)
    # close connection
    conn.close()
    return names

# returns a list of colours for each party in the database


def getColours():
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' SELECT colour FROM party '''
    colour = [id[0] for id in c.execute(sql)]
    print(colour)
    # close connection
    conn.close()
    return colour

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

# status (tweet) module


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

# delete status item from the database


def delStatus(id_str):
    # connect to it
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    sql = ''' DELETE FROM status WHERE id_str = ?'''
    c.execute(sql, (id_str,))
    print('deleting status: ')
    print(id_str)
    # commit database changes
    conn.commit()
    # close connection
    conn.close()


# flask module

# route() decorator tells Flask what URL should trigger our function
@app.route('/')
def main():
    mplist = getAllAvgEngagement()
    return render_template("index.html", mplist=mplist)

# route to refresh or initialise databse
@app.route('/refresh')
def refresh():
    intialiseDB()
    return 'database has been refreshed'


if __name__ == "__main__":
    app.run(debug=True)

test = app.instance_path
print(test)
