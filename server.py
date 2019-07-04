from flask import Flask, jsonify, render_template, request
import psycopg2

app = Flask(__name__)
uri = "postgres://meow:meow@localhost:5432/dbs"
conn = psycopg2.connect(uri)


def get_user_name(user_name):
    cur = conn.cursor()

    # execute a statement, getting all cats from database
    cur.execute("""
    SELECT * FROM "Users" WHERE "ScreenName" = %s
    """, (user_name, ))

    # return results
    user = cur.fetchone()

    print(f"fetched user {user}")
    if user is None:
        return None

    return {"id": user[0],
            "name": user[1],
            "screenName": user[2],
            "ort": user[3],
            "verified": user[4]}


def get_income(UID):
    cur = conn.cursor()

    # execute a statement, getting all cats from database
    cur.execute("""SELECT count(*)
                    FROM "Tweets"
                    WHERE "UID" = %s""", (UID, ))

    # return results
    income = cur.fetchone()
    return income[0]


def get_user_id(UID):
    cur = conn.cursor()

    # execute a statement, getting all cats from database
    cur.execute("""SELECT * FROM "Users" WHERE "UID" = %s""", (UID, ))

    # return results
    user = cur.fetchone()

    if user is None:
        return None

    return {"id": user[0],
            "name": user[1],
            "screenName": user[2],
            "ort": user[3],
            "verified": user[4]}


def get_fans(UID):
    cur = conn.cursor()

    # execute a statement, getting all cats from database
    cur.execute("""SELECT "UID" FROM "IsFanOf" WHERE "FID" = %s""", (UID, ))

    # return results
    fans = [x[0] for x in cur.fetchall()]

    return fans


def get_retweeted(UID):
    cur = conn.cursor()

    cur.execute("""SELECT "R"."TID", count("R"."TID")
                    FROM "Retweets" as "R"
                    WHERE "R"."UID" = %s
                    GROUP BY "R"."TID";
                    """, (UID, ))

    cur_res = cur.fetchall()
    retweets = {int(x[0]): x[1] for x in cur_res}

    return retweets


def get_count_retweeted(UID, TID):
    cur = conn.cursor()

    cur.execute("""SELECT count(*)
                    FROM "Retweets" as "R" 
                    WHERE "R"."TID" = %s
                    AND "R"."UID" = %s
                    AND not "R"."TID" = "R"."UID" 
                    """, (TID, UID))

    res = cur.fetchone()[0]

    return res


def get_age(UID):
    cur = conn.cursor()

    cur.execute("""SELECT age((SELECT time
                    FROM "Tweets"
                    WHERE "UID" = %s
                    ORDER BY "time" DESC
                    LIMIT 1),
                    (SELECT time
                    FROM "Tweets"
                    WHERE "UID" = %s
                    ORDER BY "time" ASC
                    LIMIT 1))
                    """, (UID, UID))

    try:
        res = cur.fetchone()[0]
        return res.days

    except Exception as e:  # not sure what happens when there is no tweet, just return 0 Days
        print(f">>Error in get_age(){e}")
        return 0


def get_all_incomes():
    cur = conn.cursor()

    cur.execute("""SELECT count(*) as income
                FROM "Tweets" T
                GROUP BY T."UID";
    """)

    try:
        return [x[0] for x in cur.fetchall()]

    except Exception as e:  # not sure what happens when there is no tweet, just return 0 Days
        print(f">>Error in get_all_incomes(){e}")
        return 0


def get_all_ages():
    cur = conn.cursor()

    cur.execute("""SELECT age(max(time), min(time)) as age
    FROM "Tweets"
    GROUP BY "UID"
    """)

    try:
        return [x[0] for x in cur.fetchall()]

    except Exception as e:  # not sure what happens when there is no tweet, just return 0 Days
        print(f">>Error in get_all_ages(){e}")
        return 0


@app.route("/")
def index():
    return render_template("index.html", data=None)


@app.route("/user")
def return_profile():

    user_name = request.args.get('user_name')

    if not user_name:  # user_name parameter was missing
        return render_template("index.html")

    if user_name.isdigit():  # check if id or screenName was supplied
        user = get_user_id(user_name)
    else:
        user = get_user_name(user_name)

    if user is None:
        return "User wasn't found"

    retweets = {
        k: {"rewteeted_x": v, "x_retweeted": get_count_retweeted(k, user.get("id"))}
        for (k, v) in get_retweeted(user.get("id")).items()
    }

    user.update({
        "Income": f"{get_income(user.get('id'))} Tweet$",
        "Age": f"{get_age(user.get('id'))} Days"
    })
    data = {"User": user,
            "Fans": [{x: f"http://localhost:8080/user?user_name={x}"} for x in get_fans(user.get("id"))],
            "Retweets": retweets,
            "Dating": [{k: f"http://localhost:8080/user?user_name={k}"}
                               for (k, v) in retweets.items() if v.get("rewteeted_x") == 1
                             and v.get("x_retweeted") == 1],
            "Married": [{k: f"http://localhost:8080/user?user_name={k}"} for (k, v) in retweets.items() if v.get("rewteeted_x") > 1
                                and v.get("x_retweeted") > 1],
            "Incomes": incomes,
            "Ages": ages}

    data["User"]["Fans"] = len(data["Fans"])
    return render_template("index.html", data=data)


incomes = get_all_incomes()
ages = get_all_ages()

# print(incomes)
# print(ages)

if __name__ == "__main__":
    # http://localhost:8080/user?user_name=1097872939951763456
    app.run("localhost", 8080, True, True)
