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

