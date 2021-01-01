import flask
from flask import request, Response
import sqlite3
import random

# The location of the database
location = "data"

# Connect to the database
conn = sqlite3.connect(location)
c = conn.cursor()

# Create table of users, with user_name, user_id, gender and pronouns columns
sql = "CREATE TABLE IF NOT EXISTS users (user_name varchar(255), first_name varchar(255), last_name varchar(255), user_id integer, gender varchar(255), pronouns varchar(255))"
c.execute(sql)
conn.commit()

# Create table of interests, with user_id and 5 interest columns
sql = "CREATE TABLE IF NOT EXISTS interests (user_id integer, interest1 varchar(255), interest2 varchar(255), interest3 varchar(255), interest4 varchar(255), interest5 varchar(255))"
c.execute(sql)
conn.commit()

# Checks if a value exists in a column of a table
# https://stackoverflow.com/a/39283198/9899381


def has_value(cursor, table, column, value):
    query = 'SELECT 1 from {} WHERE {} = ? LIMIT 1'.format(table, column)
    return cursor.execute(query, (value,)).fetchone() is not None


# Generates a random user_id
def generate_user_id():
    user_id = random.randrange(10000, 99999)
    while has_value(c, "users", "user_id", user_id):
        user_id = random.randrange(10000, 99999)
    return user_id


def check_if_user_exists(user_name):
    # The location of the database
    location = "data"

    # Connect to the database
    conn = sqlite3.connect(location)
    c = conn.cursor()

    return has_value(c, "users", "user_name", user_name)


def register_user(name, first_name, last_name, gender, pronouns, interests):
    # If user name is already in use, return False with the reason
    if check_if_user_exists(name):
        return False, "User name already in use."

    user_id = generate_user_id()

    # Insert the new user into the 'user' table
    sql = f"""INSERT INTO users
                  (user_name,
                  first_name,
                  last_name,
                  user_id,
                  gender,
                  pronouns)
              VALUES ('{name}',
                      '{first_name}',
                      '{last_name}',
                      {user_id},
                      '{gender}',
                      '{pronouns}')
          """
    c.execute(sql)
    conn.commit()

    # Insert the new user's interests into the 'interests' table
    sql = f"""INSERT INTO interests
                  (user_id,
                  interest1,
                  interest2,
                  interest3,
                  interest4,
                  interest5)
              VALUES ('{user_id}',
                      '{interests[0]}',
                      '{interests[1]}',
                      '{interests[2]}',
                      '{interests[3]}',
                      '{interests[4]}')
           """
    c.execute(sql)
    conn.commit()

    return True, "Success"


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/register', methods=['POST'])
def register():
    # The location of the database
    location = "data"

    # Connect to the database
    global conn
    global c
    conn = sqlite3.connect(location)
    c = conn.cursor()

    # Create table of users, with user_name, user_id, gender and pronouns columns
    sql = "CREATE TABLE IF NOT EXISTS users (user_name varchar(255), first_name varchar(255), last_name varchar(255), user_id integer, gender varchar(255), pronouns varchar(255))"
    c.execute(sql)
    conn.commit()

    # Create table of interests, with user_id and 5 interest columns
    sql = "CREATE TABLE IF NOT EXISTS interests (user_id integer, interest1 varchar(255), interest2 varchar(255), interest3 varchar(255), interest4 varchar(255), interest5 varchar(255))"
    c.execute(sql)
    conn.commit()

    req_data = request.get_json()

    user_name = req_data["user_name"]
    first_name = req_data["first_name"]
    last_name = req_data["last_name"]
    gender = req_data["gender"]
    pronouns = req_data["pronouns"]
    interests = req_data["interests"]

    success, message = register_user(
        user_name, first_name, last_name, gender, pronouns, interests)

    if success:
        return Response("{'message':" + message + "}", status=201, mimetype="application/json")

    return Response("{'message':" + message + "}", status=409, mimetype="application/json")


@app.route('/check_username', methods=['POST'])
def check_username():
    req_data = request.get_json()

    user_name = req_data["user_name"]

    exists = check_if_user_exists(user_name)

    if exists:
        return Response("{'message': 'User name already in use.'}", status=409, mimetype="application/json")
    return Response("{'message': 'User name available'}", status=200, mimetype="application/json")


app.run()
