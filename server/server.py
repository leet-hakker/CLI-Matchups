import flask
from flask import request, Response
from flask import jsonify, send_file
import sqlite3
import random
import bcrypt
import get_matches
from registration import registration
from login import loginblueprint
from matching import matching
import utils
import io

# The location of the database
location = "data"

# Connect to the database
conn = sqlite3.connect(location)
c = conn.cursor()

# Create table of users, with user_name, user_id, gender, pronouns, salt, hash and nonce columns
sql = "CREATE TABLE IF NOT EXISTS users (user_name varchar(255), first_name varchar(255), last_name varchar(255), gender varchar(255), pronouns varchar(255), age INT, count INT, lat REAL, lng REAL, salt varchar(255), hash varchar(255), nonce varchar(255))"
c.execute(sql)
conn.commit()

# Create table of interests, with user_id and 5 interest columns
sql = "CREATE TABLE IF NOT EXISTS interests (user_name varchar(255), interest1 varchar(255), interest2 varchar(255), interest3 varchar(255), interest4 varchar(255), interest5 varchar(255))"
c.execute(sql)
conn.commit()

c.execute("SELECT * FROM users")
index = len(c.fetchall())

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.register_blueprint(registration)
app.register_blueprint(loginblueprint)
app.register_blueprint(matching)


@app.route("/get-match", methods=["GET"])
def get_match():
    req_data = request.get_json()
    users = get_matches.get_100_sorted_users(req_data["user_name"])

    count = len(users)
    if count:
        conn = sqlite3.connect("data")
        c = conn.cursor()
        c.execute(
            "UPDATE users SET count = ? WHERE user_name=?",
            (count, req_data["user_name"]),
        )
        conn.commit()
        return jsonify(users)
    else:
        return Response(
            '{"message": "Invalid request"}', status=401, mimetype="application/json"
        )


@app.route("/confirm-match", methods=["POST"])
def confirm_match():
    req_data = request.get_json()
    return Response('{"message:" "Success"}', status=200, mimetype="application/json")


@app.route("/reject-match", methods=["POST"])
def reject_match():
    req_data = request.get_json()
    return Response('{"message": "Success"}', status=200, mimetype="application/json")


app.run()
