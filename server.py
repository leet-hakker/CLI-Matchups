import flask
from flask import request, Response
from flask import jsonify
import sqlite3
import random
import bcrypt

# The location of the database
location = "data"

# Connect to the database
conn = sqlite3.connect(location)
c = conn.cursor()

# Create table of users, with user_name, user_id, gender, pronouns, salt, hash and nonce columns
sql = "CREATE TABLE IF NOT EXISTS users (user_name varchar(255), first_name varchar(255), last_name varchar(255), gender varchar(255), pronouns varchar(255), salt varchar(255), hash varchar(255), nonce varchar(255))"
c.execute(sql)
conn.commit()

# Create table of interests, with user_id and 5 interest columns
sql = "CREATE TABLE IF NOT EXISTS interests (user_name varchar(255), interest1 varchar(255), interest2 varchar(255), interest3 varchar(255), interest4 varchar(255), interest5 varchar(255))"
c.execute(sql)
conn.commit()

# Checks if a value exists in a column of a table
# https://stackoverflow.com/a/39283198/9899381


def has_value(table, column, value):
    conn = sqlite3.connect(location)
    c = conn.cursor()
    query = "SELECT 1 from {} WHERE {} = ? LIMIT 1".format(table, column)
    return c.execute(query, (value,)).fetchone() is not None


def check_if_user_exists(user_name):
    # The location of the database
    location = "data"
    return has_value("users", "user_name", user_name)


def register_user(name, first_name, last_name, gender, pronouns, interests, auth):
    # If user name is already in use, return False with the reason
    if check_if_user_exists(name):
        return False, "User name already in use."

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(auth.encode("utf-8"), salt)
    del auth

    # Connect to the database
    conn = sqlite3.connect(location)
    c = conn.cursor()

    # Insert the new user into the 'user' table
    c.execute(
        """INSERT INTO users
                  (user_name,
                  first_name,
                  last_name,
                  gender,
                  pronouns,
                  salt,
                  hash)
              VALUES (?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?,
                      ?);""",
        (name, first_name, last_name, gender, pronouns, salt, hash),
    )
    conn.commit()

    # Insert the new user's interests into the 'interests' table
    c.execute(
        """INSERT INTO interests
                  (user_name,
                  interest1,
                  interest2,
                  interest3,
                  interest4,
                  interest5)
              VALUES (?,?,?,?,?,?);""",
        (name, interests[0], interests[1], interests[2], interests[3], interests[4]),
    )
    conn.commit()

    return True, "Success"


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/register", methods=["POST"])
def register():
    # The location of the database
    location = "data"

    # Connect to the database
    conn = sqlite3.connect(location)
    c = conn.cursor()

    req_data = request.get_json()

    user_name = req_data["user_name"]
    first_name = req_data["first_name"]
    last_name = req_data["last_name"]
    gender = req_data["gender"]
    pronouns = req_data["pronouns"]
    interests = req_data["interests"]
    auth = req_data["auth"]

    success, message = register_user(
        user_name, first_name, last_name, gender, pronouns, interests, auth
    )

    if success:
        return Response(
            "{'message':" + message + "}", status=201, mimetype="application/json"
        )

    return Response(
        "{'message':" + message + "}", status=409, mimetype="application/json"
    )


@app.route("/check_username", methods=["POST"])
def check_username():
    req_data = request.get_json()

    user_name = req_data["user_name"]

    exists = check_if_user_exists(user_name)

    if exists:
        return Response(
            "{'message': 'User name already in use.'}",
            status=409,
            mimetype="application/json",
        )
    return Response(
        "{'message': 'User name available'}", status=200, mimetype="application/json"
    )


@app.route("/login", methods=["POST"])
def login():
    # Connect to the database
    conn = sqlite3.connect("data")
    c = conn.cursor()

    req_data = request.get_json()
    username = req_data["user_name"]
    client_nonce = req_data["client_nonce"].encode("utf-8")
    client_nonce_hash = req_data["nonce_hash"].encode("utf-8")

    if not check_if_user_exists(username):
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )

    c.execute("SELECT hash,nonce FROM users WHERE user_name=?", (username,))

    password_hash, server_nonce = c.fetchone()

    c.execute("UPDATE users SET nonce = NULL WHERE user_name=?", (username,))
    conn.commit()

    # print(client_nonce)
    # print(server_nonce)
    server_nonce_hash = bcrypt.hashpw(
        password_hash, bcrypt.hashpw(client_nonce, server_nonce)
    )

    print(client_nonce_hash)

    if client_nonce_hash == server_nonce_hash:
        return Response(
            '{"message": "Authorisation accepted"}',
            status=200,
            mimetype="application/json",
        )
    else:
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )


@app.route("/salt-nonce", methods=["GET"])
def request_salt_and_nonce():
    req_data = request.get_json()
    user_name = req_data["user_name"]

    # Connect to the database
    conn = sqlite3.connect("data")
    c = conn.cursor()

    c.execute("""SELECT salt FROM users WHERE user_name=?""", (user_name,))

    salt = c.fetchone()
    nonce = bcrypt.gensalt()
    c.execute("UPDATE users SET nonce = ? WHERE user_name=?", (nonce, user_name))
    conn.commit()

    if salt is not None:
        salt = salt[0]
        string = '{"message":"' + str(salt)[2:-1] + " " + str(nonce)[2:-1] + '"}'

        return Response(string, status=200, mimetype="application/json")

    else:
        return Response(
            '{"message": "Authorisation rejected"}',
            status=401,
            mimetype="application/json",
        )


@app.route("/get-match", methods=["GET"])
def get_match():
    req_data = request.get_json()

    conn = sqlite3.connect("data")
    c = conn.cursor()

    c.execute("SELECT * FROM users ORDER BY RANDOM()")
    user = c.fetchone()

    name = user[0]
    first_name = user[1]
    last_name = user[2]
    gender = user[3]
    pronouns = user[4]

    c.execute("SELECT * FROM interests WHERE user_name=?", (name,))
    interests = c.fetchone()[1:]

    data = {
        "user_name": name,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "pronouns": pronouns,
        "interests": interests,
    }

    return jsonify(data)


@app.route("/confirm-match", methods=["POST"])
def confirm_match():
    req_data = request.get_json()
    return Response('{"message:" "Success"}', status=200, mimetype="application/json")


@app.route("/reject-match", methods=["POST"])
def reject_match():
    req_data = request.get_json()
    return Response('{"message": "Success"}', status=200, mimetype="application/json")


app.run()
