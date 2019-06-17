# return list containing:
# gender    average engagement
# male      2353
# female    2321
# need avergae engagement for all status where user_id.gender is male
# need avergae engagement for all status where user_id.gender is female


def getGenderEngagement(gender):
    # connect to db
    conn = sqlite3.connect(db)
    # get cursor
    c = conn.cursor()
    # get total retweet_count and favorite_count for user_id
    favesql = ''' SELECT sum(favorite_count) AS 'Likes' FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ?'''
    c.execute(favesql, (gender,))
    fetch = c.fetchone()
    totalfavorite = fetch[0]
    print("Total favorite: ", totalfavorite)
    # find sum of total retweet_count and favorite_count
    retweetsql = ''' SELECT sum(retweet_count) AS 'Likes' FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE gender = ?'''
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
    favesql = ''' SELECT sum(favorite_count) AS 'Likes' FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ?'''
    c.execute(favesql, (party,))
    fetch = c.fetchone()
    totalfavorite = fetch[0]
    print("Total favorite: ", totalfavorite)
    # find sum of total retweet_count and favorite_count
    retweetsql = ''' SELECT sum(retweet_count) AS 'Likes' FROM status INNER JOIN mp ON status.user_id = mp.user_id WHERE party = ?'''
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