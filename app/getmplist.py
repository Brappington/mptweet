import tweepy
import csv

# twitter api config
consumer_key = 'NtLIPnCyyeEiiEWl3LWPCNssl'
consumer_secret = 'nkOUbyh5mUeVp3pxO5mjqbBIJFxaQYNoUN0ybcPJPC3fwnEcTI'
access_token = '1090976401333858304-Vu5Y7y7KUyxpblwkzegs7VMxfKbXTt'
access_secret = 'xLZBZxojXvpPMIE4tJnylTJ7DIZLKZauLytyzSUb2Y1s6'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
slug = 'uk-mps'
owner = 'twittergov'


def get_list_members(api, owner, slug):
    members = []
    for page in tweepy.Cursor(api.list_members, owner, slug).items():
        members.append(page)
	# create a list containing all usernames
    return [m.screen_name for m in members]

# create new CSV file and add column headings


def create_csv(filename, usernames):
	csvfile = open(filename, 'w')
	c = csv.writer(csvfile)
	# write the header row for CSV file
	c.writerow(["name",
				"display_name",
				"bio",
				"followers_count",
				"following_count",
				"acct_created",
				"location"])
	# add each member to the csv
	for name in usernames:
		user_info = get_userinfo(name)
		c.writerow(user_info)
	# close and save the CSV
	csvfile.close()


def get_userinfo(name):
	# get all user data via a Tweepy API call
	user = api.get_user(screen_name=name)
	# create row data as a list
	user_info = [name.encode('utf-8'),
				user.name.encode('utf-8'),
				user.description.encode('utf-8'),
				user.followers_count,
				user.friends_count,
				user.created_at,
				user.location.encode('utf-8')]
	# send that one row back
	return user_info


def main():
	# provide name for new CSV
	filename = "userinfo.csv"
	# create list of all members of the Twitter list
	usernames = get_list_members(api, owner, slug)
	# create new CSV and fill it
	create_csv(filename, usernames)

if __name__ == '__main__':
	main()
