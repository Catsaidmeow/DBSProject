import csv
import re
import psycopg2
from psycopg2.extras import execute_values  # used for bulk insert, speeds up like crazy


def isEmpty(string):
    return (not string) or string == "None"


def connect():
    """ Create the connection """
    try:
        # connect to the PostgreSQL server using uri

        uri = "postgres://meow:meow@localhost:5432/dbs"

        print('>>Connecting to the PostgreSQL database with uri: %s' % uri)
        return psycopg2.connect(uri)

    except (Exception, psycopg2.DatabaseError) as error:
        print(">>Error: %s" % error)


def str2bool(v):
    try:
        return v.lower() in ("true", "t", "1", "yes")

    # user doesn't have verified
    except:
        return False


def getHashtags(tweet):
    regex = r"(?<=\#)(.*?)(?=(\,|\s))"
    return [x for (x, y) in re.findall(regex, tweet)]


def checkTweet(tweet):
    # print(tweet["createdAt"])
    if not tweet["tweetID"].isdigit():
        return False
    if not tweet["userID"].isdigit():
        return False
    regex = r'20\d{2}-0[1-9]|1[0-2]-(0[1-9])|([1-2][0-9])|(3[0-1])\s([0-1][1-9])|(2[0-4]):[0-5][0-9]:[0-5][0-9]'

    if not tweet["tweet"]:
        return False

    return True


def isRetweet(tweet_text):
    regex = r"(?<=RT \@).*(?=\:)"
    return bool(re.search(regex, tweet_text))


def getTIDByText(uid, text):
    for tweet in tweets:
        if tweet["userID"] == uid and tweet["tweet"] == text:
            return tweet["tweetID"]
    return None


def checkTweets():
        for tweet in tweets:
            if checkTweet(tweet):
                if isRetweet(tweet["tweet"]):
                    retweetedUser = re.search("(?<=RT \@)(.*?)(?=\:)", tweet["tweet"]).group(0)

                    retweetedUserDict = users_name_dict.get(retweetedUser)

                    if retweetedUserDict:

                        retweeted_user_id = retweetedUserDict["id"]

                        retweeted_batch.append((tweet["userID"], retweeted_user_id))

                    else:
                        continue  # there's no userId, meaning user does not exist in our data, skip entry

                else:

                    tweet_batch.append((tweet["tweetID"], tweet["userID"], tweet["tweet"], tweet["createdAt"]))

                    for hashtag in getHashtags(tweet["tweet"]):
                        hashtag_batch.append((tweet["tweetID"], hashtag))

            else:
                continue  # if tweet is not valid, drop tweet


def check_users():
    # check user data
    for user in users:

        # useriD isn't a string, this shouldn't happen, skip entry
        if (not user["id"].isdigit()) or isEmpty(user["id"]):
            continue

        # filter users without a screenName
        if isEmpty(user['screenName']):
            continue

        # filter users without a name
        if isEmpty(user["name"]):
            continue

        user_batch.append((user["id"], user["name"], user["screenName"], user["location"], str2bool(user['verified'])))

        # fill user dictionary ordered by screenName and ID
        users_name_dict[user['screenName']] = user
        users_id_dict[user["id"]] = user


def check_follows():
    # check follows data
    for follower in follows:
        uid = follower['userID']
        fid = follower["followerID"]

        # check if both are digits
        if uid.isdigit() and fid.isdigit():

            # check if both exist in our user-data
            if uid in users_id_dict and fid in users_id_dict:
                follows_batch.append((uid, fid))


def writeRetweet():
    cursor = connection.cursor()

    execute_values(cursor,
                   """INSERT INTO "Retweets" ("UID", "TID") VALUES %s ON CONFLICT DO NOTHING;""",
                   retweeted_batch,
                   page_size=500)

    connection.commit()

    cursor.close()


def writeTweet():
    cursor = connection.cursor()

    execute_values(cursor,
                   """INSERT INTO "Tweets" ("TID", "UID", "content", "time") VALUES %s ON CONFLICT DO NOTHING;""",
                   tweet_batch,
                   page_size=500)

    connection.commit()

    cursor.close()


def writeContains():
    cursor = connection.cursor()

    execute_values(cursor,
                   """INSERT INTO "Contains" ("TID", "name") VALUES %s ON CONFLICT DO NOTHING;""",
                   hashtag_batch,
                   page_size=500)

    connection.commit()


    cursor.close()


def writeUsers():
    cursor = connection.cursor()

    execute_values(cursor,
                   """INSERT INTO "Users" ("UID", "Name", "ScreenName", "Ort", "verified") VALUES %s ON CONFLICT DO NOTHING;""",
                   user_batch,
                   page_size=500)

    connection.commit()

    cursor.close()


def writeIsFanOf():
    cursor = connection.cursor()

    execute_values(cursor,
                   """INSERT INTO "IsFanOf" ("UID", "FID") VALUES %s ON CONFLICT DO NOTHING;""",
                   follows_batch,
                   page_size=500)

    connection.commit()

    cursor.close()


if __name__ == "__main__":

    connection = connect()

    tweets = csv.DictReader(open("prj_tweet.csv", "r"), dialect="excel", delimiter=";")
    users = csv.DictReader(open("prj_user.csv", 'r'), dialect="excel", delimiter=";")
    follows = csv.DictReader(open("prj_following.csv", 'r'), dialect="excel", delimiter=";")

    users_name_dict = dict()
    users_id_dict = dict()

    retweeted_batch = []
    tweet_batch = []
    user_batch = []
    hashtag_batch = []
    follows_batch = []

    print(">> iterating over users")
    check_users()

    print(">> writing users")
    writeUsers()

    print(">> iterating over followers")
    check_follows()

    print(">> writing isFanOf")
    writeIsFanOf()

    print(">> iterating over tweets")
    checkTweets()

    print(">> writing retweets")
    writeRetweet()

    print(">> writing tweets")
    writeTweet()

    print(">> writing contains")
    writeContains()

